"""
Cleanup Duplicate Vendors in Neo4j

Merges duplicate vendor nodes that have the same normalized name but different casing.
This fixes issues where vendors were loaded with inconsistent casing (e.g., "Stripe" vs "stripe").

Usage:
    python scripts/neo4j/cleanup_duplicate_vendors.py [--dry-run]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from scripts.utils import setup_logging, load_config, validate_env_vars


def merge_duplicate_vendors(driver, dry_run=False):
    """
    Find and merge duplicate vendors based on normalized name
    
    Args:
        driver: Neo4j driver instance
        dry_run: If True, only report what would be merged without making changes
    """
    logger = logging.getLogger(__name__)
    
    with driver.session() as session:
        # Find all duplicate vendors
        query = """
        MATCH (v:Vendor)
        WITH toLower(v.name) as normalized_name, collect(v) as vendors
        WHERE size(vendors) > 1
        RETURN normalized_name, vendors
        ORDER BY normalized_name
        """
        
        result = session.run(query)
        duplicates = list(result)
        
        if not duplicates:
            logger.info("✅ No duplicate vendors found!")
            return 0
        
        logger.info(f"Found {len(duplicates)} sets of duplicate vendors:")
        for record in duplicates:
            normalized_name = record['normalized_name']
            vendor_nodes = record['vendors']
            vendor_names = [v['name'] for v in vendor_nodes]
            logger.info(f"  - {normalized_name}: {vendor_names} ({len(vendor_nodes)} duplicates)")
        
        if dry_run:
            logger.info("\n🔍 DRY RUN: No changes made. Run without --dry-run to merge duplicates.")
            return 0
        
        # Merge duplicates
        logger.info("\n🔄 Merging duplicate vendors...")
        merged_count = 0
        
        for record in duplicates:
            normalized_name = record['normalized_name']
            vendor_nodes = record['vendors']
            
            # Sort by name length and casing (prefer shorter, properly cased names)
            # e.g., prefer "Stripe" over "stripe", "Auth0" over "auth0"
            vendor_nodes_sorted = sorted(
                vendor_nodes,
                key=lambda v: (
                    len(v['name']),  # Shorter names first
                    v['name'] != v['name'].capitalize(),  # Properly cased first
                    v['name']
                )
            )
            
            # Keep the first (best) vendor, merge others into it
            keep_vendor = vendor_nodes_sorted[0]
            merge_vendors = vendor_nodes_sorted[1:]
            
            keep_name = keep_vendor['name']
            keep_id = keep_vendor.id
            
            logger.info(f"  Keeping: {keep_name} (node {keep_id})")
            
            for merge_vendor in merge_vendors:
                merge_name = merge_vendor['name']
                merge_id = merge_vendor.id
                
                # Merge relationships and properties
                merge_query = """
                MATCH (keep:Vendor) WHERE id(keep) = $keep_id
                MATCH (merge:Vendor) WHERE id(merge) = $merge_id
                
                // Move all relationships from merge to keep
                WITH keep, merge
                OPTIONAL MATCH (merge)-[r1:SUPPORTS]->(bp:BusinessProcess)
                FOREACH (r IN CASE WHEN r1 IS NOT NULL THEN [r1] ELSE [] END |
                    MERGE (keep)-[:SUPPORTS]->(bp)
                    DELETE r
                )
                
                WITH keep, merge
                OPTIONAL MATCH (merge)-[r2:SATISFIES]->(cc:ComplianceControl)
                FOREACH (r IN CASE WHEN r2 IS NOT NULL THEN [r2] ELSE [] END |
                    MERGE (keep)-[:SATISFIES]->(cc)
                    DELETE r
                )
                
                WITH keep, merge
                OPTIONAL MATCH (s:Service)-[r3:DEPENDS_ON]->(merge)
                FOREACH (r IN CASE WHEN r3 IS NOT NULL THEN [r3] ELSE [] END |
                    MERGE (s)-[:DEPENDS_ON]->(keep)
                    DELETE r
                )
                
                // Update properties (keep non-null values from merge)
                WITH keep, merge
                SET keep.vendor_id = COALESCE(keep.vendor_id, merge.vendor_id),
                    keep.category = COALESCE(keep.category, merge.category),
                    keep.criticality = COALESCE(keep.criticality, merge.criticality),
                    keep.display_name = COALESCE(keep.display_name, merge.display_name)
                
                // Ensure name is set to the kept version
                SET keep.name = $keep_name
                
                // Delete the duplicate node
                DELETE merge
                
                RETURN count(*) as merged
                """
                
                session.run(
                    merge_query,
                    keep_id=keep_id,
                    merge_id=merge_id,
                    keep_name=keep_name
                )
                
                logger.info(f"    Merged: {merge_name} (node {merge_id}) → {keep_name}")
                merged_count += 1
        
        logger.info(f"\n✅ Successfully merged {merged_count} duplicate vendor nodes!")
        
        # Verify cleanup
        verify_query = """
        MATCH (v:Vendor)
        WITH toLower(v.name) as normalized_name, collect(v) as vendors
        WHERE size(vendors) > 1
        RETURN count(*) as remaining_duplicates
        """
        
        result = session.run(verify_query)
        remaining = result.single()['remaining_duplicates']
        
        if remaining == 0:
            logger.info("✅ Verification: No duplicates remaining!")
        else:
            logger.warning(f"⚠️  Verification: {remaining} sets of duplicates still remain")
        
        # Count final vendors
        count_query = "MATCH (v:Vendor) RETURN count(v) as total_vendors"
        result = session.run(count_query)
        total = result.single()['total_vendors']
        logger.info(f"📊 Total vendors in graph: {total}")
        
        return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Clean up duplicate vendor nodes in Neo4j'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be merged without making changes'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Validate environment
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Neo4j credentials not configured. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD")
        return 1
    
    # Load config
    config = load_config()
    neo4j_config = config['neo4j']
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        neo4j_config['uri'],
        auth=(neo4j_config['user'], neo4j_config['password'])
    )
    
    try:
        logger.info("🔍 Checking for duplicate vendors...")
        return merge_duplicate_vendors(driver, dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Failed to cleanup duplicates: {e}", exc_info=True)
        return 1
    finally:
        driver.close()


if __name__ == "__main__":
    exit(main())

