"""
Cleanup Duplicate Services in Neo4j

Merges duplicate service nodes that have the same GCP resource path but different service_ids.
This script should be run once to clean up existing duplicates.

Usage:
    python scripts/cleanup/cleanup_duplicate_services.py
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from scripts.utils import setup_logging, load_config, validate_env_vars

logger = logging.getLogger(__name__)


def cleanup_duplicate_services(driver):
    """
    Merge duplicate services that have the same GCP resource path
    
    Args:
        driver: Neo4j driver instance
    """
    logger.info("🔍 Finding duplicate services (same GCP resource)...")
    
    with driver.session() as session:
        # Find all services grouped by GCP resource
        result = session.run("""
            MATCH (s:Service)
            WHERE s.gcp_resource IS NOT NULL AND s.gcp_resource <> ''
            WITH s.gcp_resource as gcp_resource, collect(s) as services
            WHERE size(services) > 1
            RETURN gcp_resource, services
        """)
        
        duplicates = list(result)
        
        if not duplicates:
            logger.info("✅ No duplicate services found!")
            return
        
        logger.info(f"⚠️ Found {len(duplicates)} sets of duplicate services")
        
        for record in duplicates:
            gcp_resource = record['gcp_resource']
            services = record['services']
            
            logger.info(f"\n📋 Merging duplicates for '{gcp_resource}':")
            for service in services:
                logger.info(f"   - {service.get('name', 'Unknown')} (service_id: {service.get('service_id', 'N/A')})")
            
            # Choose the canonical service (prefer one with more properties set)
            canonical_service = None
            max_props = 0
            for service in services:
                prop_count = len([k for k in service.keys() if service[k] is not None])
                if prop_count > max_props:
                    max_props = prop_count
                    canonical_service = service
            
            if not canonical_service:
                canonical_service = services[0]
            
            canonical_id = canonical_service.id
            canonical_service_id = canonical_service.get('service_id', 'N/A')
            
            logger.info(f"   ✅ Using service_id '{canonical_service_id}' as canonical service")
            
            # Merge all relationships and properties to canonical service
            # Then delete duplicates
            for service in services:
                if service.id == canonical_id:
                    continue
                
                service_name = service.get('name', 'Unknown')
                service_id = service.get('service_id', 'N/A')
                
                # Merge DEPENDS_ON relationships
                session.run("""
                    MATCH (duplicate:Service)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Service)
                    WHERE id(canonical) = $canonical_id
                    OPTIONAL MATCH (duplicate)-[r1:DEPENDS_ON]->(v:Vendor)
                    WITH canonical, duplicate, v, r1
                    WHERE v IS NOT NULL
                    MERGE (canonical)-[:DEPENDS_ON]->(v)
                    DELETE r1
                """, duplicate_id=service.id, canonical_id=canonical_id)
                
                # Merge SUPPORTS relationships
                session.run("""
                    MATCH (duplicate:Service)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Service)
                    WHERE id(canonical) = $canonical_id
                    OPTIONAL MATCH (duplicate)-[r2:SUPPORTS]->(bp:BusinessProcess)
                    WITH canonical, duplicate, bp, r2
                    WHERE bp IS NOT NULL
                    MERGE (canonical)-[:SUPPORTS]->(bp)
                    DELETE r2
                """, duplicate_id=service.id, canonical_id=canonical_id)
                
                # Update canonical service with best properties
                session.run("""
                    MATCH (duplicate:Service)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Service)
                    WHERE id(canonical) = $canonical_id
                    
                    SET canonical.gcp_resource = $gcp_resource,
                        canonical.name = COALESCE(canonical.name, duplicate.name),
                        canonical.service_id = COALESCE(canonical.service_id, duplicate.service_id),
                        canonical.type = COALESCE(canonical.type, duplicate.type),
                        canonical.rpm = COALESCE(canonical.rpm, duplicate.rpm),
                        canonical.customers_affected = COALESCE(canonical.customers_affected, duplicate.customers_affected)
                """, duplicate_id=service.id, canonical_id=canonical_id, gcp_resource=gcp_resource)
                
                # Delete duplicate
                session.run("""
                    MATCH (duplicate:Service)
                    WHERE id(duplicate) = $duplicate_id
                    DETACH DELETE duplicate
                """, duplicate_id=service.id)
                
                logger.info(f"   🗑️  Deleted duplicate: '{service_name}' (service_id: {service_id})")
            
            # Ensure canonical service has gcp_resource set
            session.run("""
                MATCH (s:Service)
                WHERE id(s) = $canonical_id
                SET s.gcp_resource = $gcp_resource
            """, canonical_id=canonical_id, gcp_resource=gcp_resource)
        
        logger.info("\n✅ Duplicate cleanup complete!")


def verify_cleanup(driver):
    """Verify that duplicates are gone"""
    logger.info("\n🔍 Verifying cleanup...")
    
    with driver.session() as session:
        # Count services by GCP resource
        result = session.run("""
            MATCH (s:Service)
            WHERE s.gcp_resource IS NOT NULL AND s.gcp_resource <> ''
            WITH s.gcp_resource as gcp_resource, count(*) as count
            WHERE count > 1
            RETURN gcp_resource, count
        """)
        
        remaining_duplicates = list(result)
        
        if remaining_duplicates:
            logger.warning(f"⚠️ Still found {len(remaining_duplicates)} sets of duplicates:")
            for record in remaining_duplicates:
                logger.warning(f"   - {record['gcp_resource']}: {record['count']} duplicates")
        else:
            logger.info("✅ No duplicates found - cleanup successful!")
        
        # Get final counts
        result = session.run("MATCH (s:Service) RETURN count(s) as total")
        total = result.single()['total']
        
        result = session.run("""
            MATCH (s:Service)
            WHERE s.gcp_resource IS NOT NULL AND s.gcp_resource <> ''
            WITH DISTINCT s.gcp_resource as gcp_resource
            RETURN count(gcp_resource) as unique
        """)
        unique = result.single()['unique']
        
        logger.info(f"\n📊 Final counts:")
        logger.info(f"   Total service nodes: {total}")
        logger.info(f"   Unique services (by GCP resource): {unique}")
        
        if total == unique:
            logger.info("✅ Perfect! All services are unique.")
        else:
            logger.warning(f"⚠️ Still have {total - unique} duplicate nodes")


def main():
    """Main entry point"""
    setup_logging('INFO')
    
    # Validate environment
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Please configure Neo4j credentials in .env file")
        return 1
    
    config = load_config()
    neo4j_config = config['neo4j']
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        neo4j_config['uri'],
        auth=(neo4j_config['user'], neo4j_config['password'])
    )
    
    try:
        logger.info("🔧 Starting duplicate service cleanup...")
        cleanup_duplicate_services(driver)
        verify_cleanup(driver)
        return 0
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}", exc_info=True)
        return 1
    finally:
        driver.close()


if __name__ == "__main__":
    exit(main())

