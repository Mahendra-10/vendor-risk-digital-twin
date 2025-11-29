"""
Neo4j Graph Loader Script

Loads vendor dependency data into Neo4j graph database.

Graph Model:
- Nodes: Vendor, Service, BusinessProcess, ComplianceControl
- Relationships: DEPENDS_ON, SUPPORTS, SATISFIES

Usage:
    python scripts/load_graph.py --data-file data/sample/sample_dependencies.json
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from neo4j import GraphDatabase

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils import (
    setup_logging,
    load_config,
    load_json_file,
    validate_env_vars
)


class Neo4jGraphLoader:
    """Loads vendor dependency data into Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        self.logger = logging.getLogger(__name__)
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        self.logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        self.logger.warning("Clearing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.logger.info("Database cleared")
    
    def load_dependencies(self, data: Dict[str, Any]):
        """
        Load vendor dependencies into graph
        
        Args:
            data: Vendor dependency data
        """
        self.logger.info("Loading vendor dependencies into Neo4j...")
        
        with self.driver.session() as session:
            # Load vendors and services
            for vendor in data['vendors']:
                self._create_vendor(session, vendor)
                
                for service in vendor['services']:
                    self._create_service(session, service)
                    self._link_vendor_service(
                        session, 
                        vendor['vendor_id'], 
                        service['service_id'], 
                        vendor_name=vendor.get('name'),
                        gcp_resource=service.get('gcp_resource')
                    )
                    
                    # Create business processes
                    for process in service['business_processes']:
                        self._create_business_process(session, process)
                        self._link_service_process(
                            session, 
                            service['service_id'], 
                            process,
                            gcp_resource=service.get('gcp_resource')
                        )
        
        self.logger.info("✅ Data loaded successfully")
    
    def load_compliance_controls(self, data: Dict[str, Any]):
        """
        Load compliance controls into graph
        
        Args:
            data: Compliance control data
        """
        self.logger.info("Loading compliance controls...")
        
        with self.driver.session() as session:
            for vendor_name, controls in data['control_mappings'].items():
                # Create compliance controls
                for framework, control_ids in controls.items():
                    for control_id in control_ids:
                        self._create_compliance_control(session, framework, control_id)
                        self._link_vendor_control(session, vendor_name, control_id)
        
        self.logger.info("✅ Compliance controls loaded")
    
    def _create_vendor(self, session, vendor: Dict[str, Any]):
        """Create vendor node - uses MERGE on normalized name to prevent duplicates"""
        # Normalize vendor name to lowercase for case-insensitive matching
        vendor_name = vendor.get('name', 'Unknown')
        normalized_name = vendor_name.lower().strip()
        
        # Use normalized name for MERGE, but store original name
        query = """
        MERGE (v:Vendor {name: $normalized_name})
        ON CREATE SET v.vendor_id = $vendor_id,
            v.category = $category,
            v.criticality = $criticality,
            v.display_name = $display_name
        ON MATCH SET v.vendor_id = COALESCE(v.vendor_id, $vendor_id),
                     v.category = COALESCE(v.category, $category),
                     v.criticality = COALESCE(v.criticality, $criticality),
                     v.display_name = COALESCE(v.display_name, $display_name)
        """
        params = {
            'normalized_name': normalized_name,
            'vendor_id': vendor.get('vendor_id'),
            'category': vendor.get('category'),
            'criticality': vendor.get('criticality'),
            'display_name': vendor_name  # Store original casing
        }
        session.run(query, **params)
        self.logger.debug(f"Created/updated vendor: {vendor_name} (normalized: {normalized_name})")
    
    def _create_service(self, session, service: Dict[str, Any]):
        """Create service node - uses MERGE on gcp_resource to prevent duplicates"""
        # Use GCP resource path as the unique identifier (more reliable than service_id)
        gcp_resource = service.get('gcp_resource', '')
        
        query = """
        MERGE (s:Service {gcp_resource: $gcp_resource})
        ON CREATE SET s.service_id = $service_id,
            s.name = $name,
            s.type = $type,
            s.rpm = $rpm,
            s.customers_affected = $customers_affected
        ON MATCH SET s.service_id = COALESCE(s.service_id, $service_id),
                     s.name = COALESCE(s.name, $name),
                     s.type = COALESCE(s.type, $type),
                     s.rpm = COALESCE(s.rpm, $rpm),
                     s.customers_affected = COALESCE(s.customers_affected, $customers_affected)
        """
        session.run(query, **service)
        self.logger.debug(f"Created/updated service: {service['name']} (gcp_resource: {gcp_resource})")
    
    def _create_business_process(self, session, process_name: str):
        """Create business process node"""
        query = """
        MERGE (bp:BusinessProcess {name: $name})
        """
        session.run(query, name=process_name)
        self.logger.debug(f"Created business process: {process_name}")
    
    def _create_compliance_control(self, session, framework: str, control_id: str):
        """Create compliance control node"""
        query = """
        MERGE (cc:ComplianceControl {control_id: $control_id})
        SET cc.framework = $framework
        """
        session.run(query, control_id=control_id, framework=framework)
        self.logger.debug(f"Created control: {control_id}")
    
    def _link_vendor_service(self, session, vendor_id: str, service_id: str, vendor_name: str = None, gcp_resource: str = None):
        """Create relationship: Vendor -> Service"""
        # Use GCP resource if available (most reliable), fallback to service_id
        # Normalize vendor name for case-insensitive matching
        if vendor_name:
            normalized_vendor_name = vendor_name.lower().strip()
            if gcp_resource:
                # Use GCP resource for matching (most reliable)
                query = """
                MATCH (v:Vendor {name: $normalized_vendor_name})
                MATCH (s:Service {gcp_resource: $gcp_resource})
                MERGE (s)-[:DEPENDS_ON]->(v)
                """
                session.run(query, normalized_vendor_name=normalized_vendor_name, gcp_resource=gcp_resource)
            else:
                # Fallback to service_id
                query = """
                MATCH (v:Vendor {name: $normalized_vendor_name})
                MATCH (s:Service {service_id: $service_id})
                MERGE (s)-[:DEPENDS_ON]->(v)
                """
                session.run(query, normalized_vendor_name=normalized_vendor_name, service_id=service_id)
        else:
            if gcp_resource:
                query = """
                MATCH (v:Vendor {vendor_id: $vendor_id})
                MATCH (s:Service {gcp_resource: $gcp_resource})
                MERGE (s)-[:DEPENDS_ON]->(v)
                """
                session.run(query, vendor_id=vendor_id, gcp_resource=gcp_resource)
            else:
                query = """
                MATCH (v:Vendor {vendor_id: $vendor_id})
                MATCH (s:Service {service_id: $service_id})
                MERGE (s)-[:DEPENDS_ON]->(v)
                """
                session.run(query, vendor_id=vendor_id, service_id=service_id)
    
    def _link_service_process(self, session, service_id: str, process_name: str, gcp_resource: str = None):
        """Create relationship: Service -> BusinessProcess"""
        if gcp_resource:
            query = """
            MATCH (s:Service {gcp_resource: $gcp_resource})
            MATCH (bp:BusinessProcess {name: $process_name})
            MERGE (s)-[:SUPPORTS]->(bp)
            """
            session.run(query, gcp_resource=gcp_resource, process_name=process_name)
        else:
            query = """
            MATCH (s:Service {service_id: $service_id})
            MATCH (bp:BusinessProcess {name: $process_name})
            MERGE (s)-[:SUPPORTS]->(bp)
            """
            session.run(query, service_id=service_id, process_name=process_name)
    
    def _link_vendor_control(self, session, vendor_name: str, control_id: str):
        """Create relationship: Vendor -> ComplianceControl"""
        # Normalize vendor name for case-insensitive matching
        normalized_vendor_name = vendor_name.lower().strip()
        query = """
        MATCH (v:Vendor {name: $normalized_vendor_name})
        MATCH (cc:ComplianceControl {control_id: $control_id})
        MERGE (v)-[:SATISFIES]->(cc)
        """
        session.run(query, normalized_vendor_name=normalized_vendor_name, control_id=control_id)
    
    def verify_graph(self) -> Dict[str, int]:
        """
        Verify graph was loaded correctly
        
        Returns:
            Dictionary with node and relationship counts
        """
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes
            for label in ['Vendor', 'Service', 'BusinessProcess', 'ComplianceControl']:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[f"{label}_count"] = result.single()['count']
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['relationship_count'] = result.single()['count']
        
        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Load vendor dependencies into Neo4j'
    )
    parser.add_argument(
        '--data-file',
        default='data/sample/sample_dependencies.json',
        help='Path to vendor dependency JSON file'
    )
    parser.add_argument(
        '--compliance-file',
        default='data/sample/compliance_controls.json',
        help='Path to compliance controls JSON file'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear database before loading'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    parser.add_argument(
        '--from-gcp',
        action='store_true',
        help='Load data from latest GCP discovery results in Cloud Storage'
    )
    parser.add_argument(
        '--project-id',
        help='GCP project ID (required when using --from-gcp)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Validate environment
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Please configure Neo4j credentials in .env file")
        return 1
    
    # If loading from GCP, fetch and convert discovery results
    if args.from_gcp:
        if not args.project_id:
            args.project_id = os.getenv('GCP_PROJECT_ID')
        if not args.project_id:
            logger.error("--project-id is required when using --from-gcp")
            return 1
        
        logger.info("Fetching discovery results from GCP Cloud Storage...")
        try:
            from scripts.fetch_discovery_results import get_latest_discovery, convert_to_neo4j_format
            
            discovery_results = get_latest_discovery(args.project_id)
            if not discovery_results:
                logger.error("Failed to fetch discovery results from GCP")
                return 1
            
            dependency_data = convert_to_neo4j_format(discovery_results, args.project_id)
            logger.info("✅ Successfully fetched and converted GCP discovery results")
        except Exception as e:
            logger.error(f"Failed to fetch from GCP: {e}", exc_info=True)
            return 1
    else:
        # Load dependency data from file
        logger.info(f"Loading dependency data from: {args.data_file}")
        dependency_data = load_json_file(args.data_file)
    
    # Load configuration
    config = load_config()
    neo4j_config = config['neo4j']
    
    # Initialize loader
    loader = None
    try:
        loader = Neo4jGraphLoader(
            uri=neo4j_config['uri'],
            user=neo4j_config['user'],
            password=neo4j_config['password']
        )
        
        # Clear database if requested
        if args.clear:
            loader.clear_database()
        
        # Load dependency data
        loader.load_dependencies(dependency_data)
        
        # Load compliance data
        logger.info(f"Loading compliance data from: {args.compliance_file}")
        compliance_data = load_json_file(args.compliance_file)
        loader.load_compliance_controls(compliance_data)
        
        # Verify
        stats = loader.verify_graph()
        logger.info("✅ Graph loaded successfully!")
        logger.info(f"   - Vendors: {stats['Vendor_count']}")
        logger.info(f"   - Services: {stats['Service_count']}")
        logger.info(f"   - Business Processes: {stats['BusinessProcess_count']}")
        logger.info(f"   - Compliance Controls: {stats['ComplianceControl_count']}")
        logger.info(f"   - Relationships: {stats['relationship_count']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Failed to load graph: {e}", exc_info=True)
        return 1
    
    finally:
        if loader:
            loader.close()


if __name__ == "__main__":
    exit(main())

