"""
Cloud Function: Graph Loader (Pub/Sub Subscriber)

Subscribes to vendor-discovery-events and automatically loads discovery results into Neo4j.

Trigger: Pub/Sub topic 'vendor-discovery-events'
"""

import json
import logging
import os
import base64
import sys
from pathlib import Path
from typing import Dict, Any
from google.cloud import storage
from google.cloud import pubsub_v1
from neo4j import GraphDatabase

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_neo4j_credentials() -> Dict[str, str]:
    """Get Neo4j credentials from environment variables (injected from Secret Manager)"""
    try:
        # Credentials are injected as environment variables by Cloud Functions
        # when using --set-secrets flag
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
        
        if not uri or not password:
            raise ValueError("Neo4j credentials not configured. NEO4J_URI and NEO4J_PASSWORD must be set.")
        
        logger.info(f"✅ Neo4j credentials loaded (URI: {uri[:50]}...)")
        return {'uri': uri, 'user': user, 'password': password}
    except Exception as e:
        logger.error(f"Failed to get Neo4j credentials: {e}")
        raise


def fetch_discovery_from_storage(storage_path: str, project_id: str) -> Dict[str, Any]:
    """
    Fetch discovery results from Cloud Storage
    
    Args:
        storage_path: GCS path (gs://bucket/path)
        project_id: GCP project ID
    
    Returns:
        Discovery results dictionary
    """
    try:
        # Parse GCS path
        if not storage_path.startswith('gs://'):
            raise ValueError(f"Invalid storage path: {storage_path}")
        
        path_parts = storage_path.replace('gs://', '').split('/', 1)
        bucket_name = path_parts[0]
        blob_name = path_parts[1] if len(path_parts) > 1 else ''
        
        # Download from Cloud Storage
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        content = blob.download_as_text()
        results = json.loads(content)
        
        logger.info(f"✅ Fetched discovery results from {storage_path}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to fetch from Cloud Storage: {e}")
        raise


def convert_to_neo4j_format(discovery_data: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """
    Convert GCP discovery format to Neo4j graph format
    
    Args:
        discovery_data: Raw discovery results
        project_id: GCP project ID
    
    Returns:
        Neo4j-compatible format
    """
    # Convert discovery format to Neo4j format inline (avoid import issues)
    vendors = []
    
    for vendor_data in discovery_data.get('vendors', []):
        vendor_name = vendor_data.get('name', 'Unknown')
        vendor_id = vendor_name.lower().replace(' ', '_')
        
        # Extract services from dependencies
        services = []
        for dep in vendor_data.get('dependencies', []):
            service_name = dep.get('service_name', 'Unknown')
            # Extract just the service name from full GCP resource path
            if '/' in service_name:
                service_name = service_name.split('/')[-1]
            
            service_id = service_name.lower().replace(' ', '_').replace('-', '_')
            
            services.append({
                'service_id': service_id,
                'name': service_name,
                'type': dep.get('resource_type', 'unknown'),
                'business_processes': []  # Can be enhanced later
            })
        
        vendors.append({
            'vendor_id': vendor_id,
            'name': vendor_name,
            'category': vendor_data.get('category', 'unknown'),
            'criticality': vendor_data.get('criticality', 'medium'),
            'services': services
        })
    
    return {'vendors': vendors}


def load_into_neo4j(data: Dict[str, Any], credentials: Dict[str, str]) -> None:
    """
    Load vendor dependency data into Neo4j
    
    Args:
        data: Vendor dependency data in Neo4j format
        credentials: Neo4j connection credentials
    """
    driver = None
    try:
        driver = GraphDatabase.driver(
            credentials['uri'],
            auth=(credentials['user'], credentials['password'])
        )
        
        with driver.session() as session:
            # Load vendors and services
            for vendor in data.get('vendors', []):
                vendor_id = vendor.get('vendor_id', vendor.get('name', '').lower().replace(' ', '_'))
                vendor_name = vendor.get('name', '')
                
                # Create vendor node
                session.run(
                    """
                    MERGE (v:Vendor {vendor_id: $vendor_id})
                    SET v.name = $name,
                        v.category = $category,
                        v.criticality = $criticality
                    """,
                    vendor_id=vendor_id,
                    name=vendor_name,
                    category=vendor.get('category', 'unknown'),
                    criticality=vendor.get('criticality', 'medium')
                )
                
                # Create services and relationships
                for service in vendor.get('services', []):
                    service_id = service.get('service_id', service.get('name', '').lower().replace(' ', '_'))
                    service_name = service.get('name', '')
                    
                    # Create service node
                    session.run(
                        """
                        MERGE (s:Service {service_id: $service_id})
                        SET s.name = $name,
                            s.type = $type
                        """,
                        service_id=service_id,
                        name=service_name,
                        type=service.get('type', 'unknown')
                    )
                    
                    # Create DEPENDS_ON relationship
                    session.run(
                        """
                        MATCH (v:Vendor {vendor_id: $vendor_id})
                        MATCH (s:Service {service_id: $service_id})
                        MERGE (s)-[:DEPENDS_ON]->(v)
                        """,
                        vendor_id=vendor_id,
                        service_id=service_id
                    )
        
        logger.info("✅ Successfully loaded discovery data into Neo4j")
        
    except Exception as e:
        logger.error(f"Failed to load into Neo4j: {e}", exc_info=True)
        raise
    finally:
        if driver:
            driver.close()


def load_discovery_to_neo4j(event: Dict[str, Any], context) -> None:
    """
    Cloud Function entry point for Pub/Sub trigger
    
    Args:
        event: Pub/Sub event
        context: Function context
    """
    try:
        # Decode Pub/Sub message
        if 'data' in event:
            message_data = base64.b64decode(event['data']).decode('utf-8')
            event_data = json.loads(message_data)
        else:
            event_data = event
        
        project_id = event_data.get('project_id') or os.getenv('GCP_PROJECT_ID')
        storage_path = event_data.get('storage_path')
        
        if not project_id:
            raise ValueError("project_id not found in event or environment")
        if not storage_path:
            raise ValueError("storage_path not found in event")
        
        logger.info(f"📥 Received discovery event for project: {project_id}")
        logger.info(f"   Storage path: {storage_path}")
        
        # Get Neo4j credentials
        credentials = get_neo4j_credentials()
        
        # Fetch discovery results from Cloud Storage
        discovery_data = fetch_discovery_from_storage(storage_path, project_id)
        
        # Convert to Neo4j format
        neo4j_data = convert_to_neo4j_format(discovery_data, project_id)
        
        # Load into Neo4j
        load_into_neo4j(neo4j_data, credentials)
        
        logger.info("✅ Discovery data successfully loaded into Neo4j")
        
    except Exception as e:
        logger.error(f"❌ Failed to load discovery to Neo4j: {e}", exc_info=True)
        # Re-raise to trigger Pub/Sub retry
        raise


# For local testing
if __name__ == "__main__":
    # Test with sample event
    test_event = {
        'data': base64.b64encode(json.dumps({
            'project_id': os.getenv('GCP_PROJECT_ID', 'vendor-risk-digital-twin'),
            'storage_path': 'gs://vendor-risk-digital-twin-discovery-results/discoveries/test.json'
        }).encode('utf-8')).decode('utf-8')
    }
    load_discovery_to_neo4j(test_event, None)

