"""
Check actual vendor and service counts in Neo4j

This script queries Neo4j to get accurate counts of vendors and services,
including information about duplicates.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from scripts.utils import load_config, setup_logging, validate_env_vars

def check_counts():
    """Check vendor and service counts in Neo4j"""
    
    # Setup
    logger = setup_logging()
    
    # Validate environment
    if not validate_env_vars(['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']):
        logger.error("Please configure Neo4j credentials in .env file")
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
        with driver.session() as session:
            # Get total vendor count
            result = session.run("MATCH (v:Vendor) RETURN count(v) as count")
            total_vendors = result.single()['count']
            
            # Get distinct vendor names (case-insensitive)
            result = session.run("""
                MATCH (v:Vendor)
                RETURN DISTINCT toLower(v.name) as normalized_name, 
                       collect(DISTINCT v.name) as names
                ORDER BY normalized_name
            """)
            
            vendor_details = []
            for record in result:
                normalized = record['normalized_name']
                names = record['names']
                vendor_details.append({
                    'normalized': normalized,
                    'names': names,
                    'count': len(names)
                })
            
            # Get total service count
            result = session.run("MATCH (s:Service) RETURN count(s) as count")
            total_services = result.single()['count']
            
            # Get distinct service names
            result = session.run("""
                MATCH (s:Service)
                RETURN DISTINCT s.name as name
                ORDER BY name
            """)
            service_names = [record['name'] for record in result]
            
            # Count unique vendors (case-insensitive)
            unique_vendors = len(vendor_details)
            
            # Print results
            print("\n" + "="*60)
            print("📊 NEO4J DATABASE COUNTS")
            print("="*60)
            print(f"\n📦 VENDORS:")
            print(f"   Total nodes: {total_vendors}")
            print(f"   Unique vendors (case-insensitive): {unique_vendors}")
            
            if total_vendors > unique_vendors:
                print(f"\n   ⚠️  Found {total_vendors - unique_vendors} duplicate vendor nodes!")
                print("\n   Duplicate details:")
                for detail in vendor_details:
                    if detail['count'] > 1:
                        print(f"      • {detail['normalized']}: {detail['names']} ({detail['count']} nodes)")
            
            print(f"\n   Vendor list:")
            for detail in vendor_details:
                canonical_name = detail['names'][0]  # Use first occurrence as canonical
                print(f"      • {canonical_name}")
            
            print(f"\n🔧 SERVICES:")
            print(f"   Total services: {total_services}")
            print(f"   Unique service names: {len(service_names)}")
            
            if total_services > len(service_names):
                print(f"\n   ⚠️  Found {total_services - len(service_names)} duplicate service nodes!")
            
            print(f"\n   Service list:")
            for name in service_names[:20]:  # Show first 20
                print(f"      • {name}")
            if len(service_names) > 20:
                print(f"      ... and {len(service_names) - 20} more")
            
            # Get relationship counts
            result = session.run("""
                MATCH (s:Service)-[:DEPENDS_ON]->(v:Vendor)
                RETURN count(*) as count
            """)
            depends_on_count = result.single()['count']
            
            print(f"\n🔗 RELATIONSHIPS:")
            print(f"   Service -> Vendor (DEPENDS_ON): {depends_on_count}")
            
            print("\n" + "="*60)
            print(f"\n✅ ACTUAL COUNTS:")
            print(f"   Vendors: {unique_vendors}")
            print(f"   Services: {len(service_names)}")
            print("="*60 + "\n")
            
    finally:
        driver.close()
    
    return 0

if __name__ == '__main__':
    sys.exit(check_counts())

