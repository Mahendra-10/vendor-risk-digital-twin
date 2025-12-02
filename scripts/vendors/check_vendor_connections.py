#!/usr/bin/env python3
"""
Diagnostic script to check vendor connections in Neo4j
Shows which vendors have services linked to them
"""

import sys
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils import load_config, setup_logging

load_dotenv()

def check_vendor_connections():
    """Check which vendors have services connected"""
    logger = setup_logging("INFO")
    
    config = load_config()
    neo4j_config = config['neo4j']
    
    driver = GraphDatabase.driver(
        neo4j_config['uri'],
        auth=(neo4j_config['user'], neo4j_config['password'])
    )
    
    try:
        with driver.session() as session:
            # Get all vendors with their service counts
            query = """
            MATCH (v:Vendor)
            OPTIONAL MATCH (v)<-[:DEPENDS_ON]-(s:Service)
            RETURN v.name as vendor_name,
                   v.display_name as display_name,
                   count(DISTINCT s) as service_count,
                   collect(DISTINCT s.name) as services
            ORDER BY service_count DESC, v.name
            """
            
            result = session.run(query)
            
            print("\n" + "="*80)
            print("VENDOR CONNECTION DIAGNOSTICS")
            print("="*80)
            print(f"{'Vendor Name':<20} {'Display Name':<20} {'Services':<10} {'Service Names'}")
            print("-"*80)
            
            vendors_with_services = 0
            vendors_without_services = 0
            
            for record in result:
                vendor_name = record['vendor_name']
                display_name = record['display_name'] or ''
                service_count = record['service_count']
                services = record['services'] or []
                
                if service_count > 0:
                    vendors_with_services += 1
                    status = "✓"
                else:
                    vendors_without_services += 1
                    status = "✗"
                
                services_str = ', '.join(services[:3])
                if len(services) > 3:
                    services_str += f" ... (+{len(services)-3} more)"
                
                print(f"{status} {vendor_name:<18} {display_name:<20} {service_count:<10} {services_str}")
            
            print("-"*80)
            print(f"\nSummary:")
            print(f"  Vendors with services: {vendors_with_services}")
            print(f"  Vendors without services: {vendors_without_services}")
            
            # Check specific vendor (Auth0)
            print("\n" + "="*80)
            print("AUTH0 SPECIFIC CHECK")
            print("="*80)
            
            auth0_queries = [
                ("Vendor node exists?", "MATCH (v:Vendor {name: 'auth0'}) RETURN v.name as name, v.display_name as display_name"),
                ("Services linked to auth0?", "MATCH (v:Vendor {name: 'auth0'})<-[:DEPENDS_ON]-(s:Service) RETURN s.name as service_name, s.type as service_type"),
                ("All vendors with 'auth' in name?", "MATCH (v:Vendor) WHERE toLower(v.name) CONTAINS 'auth' OR toLower(COALESCE(v.display_name, '')) CONTAINS 'auth' RETURN v.name as name, v.display_name as display_name"),
            ]
            
            for label, query in auth0_queries:
                print(f"\n{label}")
                result = session.run(query)
                records = list(result)
                if records:
                    for record in records:
                        print(f"  {dict(record)}")
                else:
                    print("  No results found")
            
    finally:
        driver.close()

if __name__ == "__main__":
    check_vendor_connections()
