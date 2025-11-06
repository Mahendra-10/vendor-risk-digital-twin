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
                    self._link_vendor_service(session, vendor['vendor_id'], service['service_id'])
                    
                    # Create business processes
                    for process in service['business_processes']:
                        self._create_business_process(session, process)
                        self._link_service_process(session, service['service_id'], process)
        
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
        """Create vendor node"""
        query = """
        MERGE (v:Vendor {vendor_id: $vendor_id})
        SET v.name = $name,
            v.category = $category,
            v.criticality = $criticality
        """
        session.run(query, **vendor)
        self.logger.debug(f"Created vendor: {vendor['name']}")
    
    def _create_service(self, session, service: Dict[str, Any]):
        """Create service node"""
        query = """
        MERGE (s:Service {service_id: $service_id})
        SET s.name = $name,
            s.type = $type,
            s.gcp_resource = $gcp_resource,
            s.rpm = $rpm,
            s.customers_affected = $customers_affected
        """
        session.run(query, **service)
        self.logger.debug(f"Created service: {service['name']}")
    
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
    
    def _link_vendor_service(self, session, vendor_id: str, service_id: str):
        """Create relationship: Vendor -> Service"""
        query = """
        MATCH (v:Vendor {vendor_id: $vendor_id})
        MATCH (s:Service {service_id: $service_id})
        MERGE (s)-[:DEPENDS_ON]->(v)
        """
        session.run(query, vendor_id=vendor_id, service_id=service_id)
    
    def _link_service_process(self, session, service_id: str, process_name: str):
        """Create relationship: Service -> BusinessProcess"""
        query = """
        MATCH (s:Service {service_id: $service_id})
        MATCH (bp:BusinessProcess {name: $process_name})
        MERGE (s)-[:SUPPORTS]->(bp)
        """
        session.run(query, service_id=service_id, process_name=process_name)
    
    def _link_vendor_control(self, session, vendor_name: str, control_id: str):
        """Create relationship: Vendor -> ComplianceControl"""
        query = """
        MATCH (v:Vendor {name: $vendor_name})
        MATCH (cc:ComplianceControl {control_id: $control_id})
        MERGE (v)-[:SATISFIES]->(cc)
        """
        session.run(query, vendor_name=vendor_name, control_id=control_id)
    
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
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Validate environment
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Please configure Neo4j credentials in .env file")
        return 1
    
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
        logger.info(f"Loading dependency data from: {args.data_file}")
        dependency_data = load_json_file(args.data_file)
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

