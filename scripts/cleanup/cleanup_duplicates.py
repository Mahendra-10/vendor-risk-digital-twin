"""
Cleanup Duplicate Vendors in Neo4j

Merges duplicate vendor nodes that differ only by case (e.g., "Stripe" and "stripe").
This script should be run once to clean up existing duplicates before reloading data.

Usage:
    python scripts/cleanup/cleanup_duplicates.py
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from scripts.utils import setup_logging, load_config, validate_env_vars

logger = logging.getLogger(__name__)


def cleanup_duplicate_vendors(driver):
    """
    Merge duplicate vendors that differ only by case
    
    Args:
        driver: Neo4j driver instance
    """
    logger.info("🔍 Finding duplicate vendors (case variations)...")
    
    with driver.session() as session:
        # Find all vendors grouped by lowercase name
        result = session.run("""
            MATCH (v:Vendor)
            WITH toLower(v.name) as normalized_name, collect(v) as vendors
            WHERE size(vendors) > 1
            RETURN normalized_name, vendors
        """)
        
        duplicates = list(result)
        
        if not duplicates:
            logger.info("✅ No duplicate vendors found!")
            return
        
        logger.info(f"⚠️ Found {len(duplicates)} sets of duplicate vendors")
        
        for record in duplicates:
            normalized_name = record['normalized_name']
            vendors = record['vendors']
            
            logger.info(f"\n📋 Merging duplicates for '{normalized_name}':")
            for vendor in vendors:
                logger.info(f"   - {vendor['name']} (id: {vendor.id})")
            
            # Choose the canonical vendor (prefer one with display_name, or first one)
            canonical_vendor = None
            for vendor in vendors:
                if 'display_name' in vendor:
                    canonical_vendor = vendor
                    break
            if not canonical_vendor:
                canonical_vendor = vendors[0]
            
            canonical_name = canonical_vendor['name']
            canonical_id = canonical_vendor.id
            
            logger.info(f"   ✅ Using '{canonical_name}' as canonical vendor")
            
            # Merge all relationships and properties to canonical vendor
            # Then delete duplicates
            for vendor in vendors:
                if vendor.id == canonical_id:
                    continue
                
                vendor_name = vendor['name']
                
                # Merge DEPENDS_ON relationships
                session.run("""
                    MATCH (duplicate:Vendor)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Vendor)
                    WHERE id(canonical) = $canonical_id
                    OPTIONAL MATCH (s:Service)-[r1:DEPENDS_ON]->(duplicate)
                    WITH canonical, duplicate, s, r1
                    WHERE s IS NOT NULL
                    MERGE (s)-[:DEPENDS_ON]->(canonical)
                    DELETE r1
                """, duplicate_id=vendor.id, canonical_id=canonical_id)
                
                # Merge SATISFIES relationships
                session.run("""
                    MATCH (duplicate:Vendor)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Vendor)
                    WHERE id(canonical) = $canonical_id
                    OPTIONAL MATCH (duplicate)-[r2:SATISFIES]->(cc:ComplianceControl)
                    WITH canonical, duplicate, cc, r2
                    WHERE cc IS NOT NULL
                    MERGE (canonical)-[:SATISFIES]->(cc)
                    DELETE r2
                """, duplicate_id=vendor.id, canonical_id=canonical_id)
                
                # Update canonical vendor with best properties
                session.run("""
                    MATCH (duplicate:Vendor)
                    WHERE id(duplicate) = $duplicate_id
                    MATCH (canonical:Vendor)
                    WHERE id(canonical) = $canonical_id
                    
                    SET canonical.name = $normalized_name,
                        canonical.display_name = COALESCE(canonical.display_name, $canonical_name),
                        canonical.vendor_id = COALESCE(canonical.vendor_id, duplicate.vendor_id),
                        canonical.category = COALESCE(canonical.category, duplicate.category),
                        canonical.criticality = COALESCE(canonical.criticality, duplicate.criticality)
                """, duplicate_id=vendor.id, canonical_id=canonical_id,
                    normalized_name=normalized_name, canonical_name=canonical_name)
                
                # Delete duplicate
                session.run("""
                    MATCH (duplicate:Vendor)
                    WHERE id(duplicate) = $duplicate_id
                    DETACH DELETE duplicate
                """, duplicate_id=vendor.id)
                
                logger.info(f"   🗑️  Deleted duplicate: '{vendor_name}'")
            
            # Ensure canonical vendor has normalized name (lowercase)
            session.run("""
                MATCH (v:Vendor)
                WHERE id(v) = $canonical_id
                SET v.name = $normalized_name,
                    v.display_name = COALESCE(v.display_name, $canonical_name)
            """, canonical_id=canonical_id, normalized_name=normalized_name, 
                canonical_name=canonical_name)
        
        # Normalize all remaining vendors to lowercase (even if they weren't duplicates)
        logger.info("\n🔄 Normalizing all vendor names to lowercase...")
        session.run("""
            MATCH (v:Vendor)
            WHERE v.name <> toLower(v.name)
            SET v.display_name = COALESCE(v.display_name, v.name),
                v.name = toLower(v.name)
        """)
        logger.info("✅ All vendor names normalized")
        
        logger.info("\n✅ Duplicate cleanup complete!")


def verify_cleanup(driver):
    """Verify that duplicates are gone"""
    logger.info("\n🔍 Verifying cleanup...")
    
    with driver.session() as session:
        # Count vendors by normalized name
        result = session.run("""
            MATCH (v:Vendor)
            WITH toLower(v.name) as normalized_name, count(*) as count
            WHERE count > 1
            RETURN normalized_name, count
        """)
        
        remaining_duplicates = list(result)
        
        if remaining_duplicates:
            logger.warning(f"⚠️ Still found {len(remaining_duplicates)} sets of duplicates:")
            for record in remaining_duplicates:
                logger.warning(f"   - {record['normalized_name']}: {record['count']} duplicates")
        else:
            logger.info("✅ No duplicates found - cleanup successful!")
        
        # Get final counts
        result = session.run("MATCH (v:Vendor) RETURN count(v) as total")
        total = result.single()['total']
        
        result = session.run("""
            MATCH (v:Vendor)
            WITH DISTINCT toLower(v.name) as normalized_name
            RETURN count(normalized_name) as unique
        """)
        unique = result.single()['unique']
        
        logger.info(f"\n📊 Final counts:")
        logger.info(f"   Total vendor nodes: {total}")
        logger.info(f"   Unique vendors: {unique}")
        
        if total == unique:
            logger.info("✅ Perfect! All vendors are unique.")
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
        logger.info("🔧 Starting duplicate vendor cleanup...")
        cleanup_duplicate_vendors(driver)
        verify_cleanup(driver)
        return 0
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}", exc_info=True)
        return 1
    finally:
        driver.close()


if __name__ == "__main__":
    exit(main())

