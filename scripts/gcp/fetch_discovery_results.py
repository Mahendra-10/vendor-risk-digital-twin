"""
Fetch Discovery Results from Cloud Storage

Fetches the latest discovery results from Cloud Storage and converts them
to the format expected by load_graph.py for Neo4j import.

Usage:
    python scripts/gcp/fetch_discovery_results.py --project-id PROJECT_ID [--output-file OUTPUT.json]
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.cloud import storage
from scripts.utils import setup_logging, load_config

logger = logging.getLogger(__name__)


def get_latest_discovery(project_id: str, bucket_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch the latest discovery results from Cloud Storage
    
    Args:
        project_id: GCP project ID
        bucket_name: Optional bucket name (defaults to {project_id}-discovery-results)
    
    Returns:
        Discovery results dictionary or None if not found
    """
    if not bucket_name:
        bucket_name = f'{project_id}-discovery-results'
    
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(bucket_name)
        
        if not bucket.exists():
            logger.error(f"Bucket {bucket_name} does not exist")
            return None
        
        # List all discovery files
        blobs = bucket.list_blobs(prefix='discoveries/')
        discovery_files = [
            blob for blob in blobs 
            if blob.name.endswith('_discovery.json')
        ]
        
        if not discovery_files:
            logger.warning(f"No discovery files found in {bucket_name}/discoveries/")
            return None
        
        # Get the latest file (by name, which includes timestamp)
        latest_blob = max(discovery_files, key=lambda b: b.name)
        logger.info(f"Fetching latest discovery: {latest_blob.name}")
        
        # Download and parse JSON
        content = latest_blob.download_as_text()
        results = json.loads(content)
        
        logger.info(f"✅ Successfully fetched discovery results from {latest_blob.name}")
        return results
    
    except Exception as e:
        logger.error(f"Failed to fetch discovery results: {e}", exc_info=True)
        return None


def convert_to_neo4j_format(discovery_results: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """
    Convert discovery results to Neo4j load format
    
    Args:
        discovery_results: Raw discovery results from Cloud Function
        project_id: GCP project ID
    
    Returns:
        Dictionary in format expected by load_graph.py
    """
    logger.info("Converting discovery results to Neo4j format...")
    
    # Vendor metadata (you can extend this with actual vendor data)
    vendor_metadata = {
        'Stripe': {
            'category': 'payment_processor',
            'criticality': 'critical',
            'business_processes': ['checkout', 'refunds', 'subscription_billing'],
            'rpm': 500,
            'customers_affected': 50000
        },
        'Auth0': {
            'category': 'authentication',
            'criticality': 'critical',
            'business_processes': ['user_login', 'user_registration', 'password_reset'],
            'rpm': 300,
            'customers_affected': 100000
        },
        'SendGrid': {
            'category': 'email_service',
            'criticality': 'high',
            'business_processes': ['email_notifications', 'transactional_emails'],
            'rpm': 200,
            'customers_affected': 25000
        },
        'Twilio': {
            'category': 'communication',
            'criticality': 'high',
            'business_processes': ['sms_notifications', '2fa_verification'],
            'rpm': 150,
            'customers_affected': 30000
        },
        'Datadog': {
            'category': 'monitoring',
            'criticality': 'medium',
            'business_processes': ['system_monitoring', 'alerting'],
            'rpm': 100,
            'customers_affected': 0
        },
        'MongoDB': {
            'category': 'database',
            'criticality': 'critical',
            'business_processes': ['data_storage', 'data_retrieval'],
            'rpm': 1000,
            'customers_affected': 0
        },
        'PayPal': {
            'category': 'payment_processor',
            'criticality': 'critical',
            'business_processes': ['checkout', 'refunds'],
            'rpm': 400,
            'customers_affected': 40000
        },
        'Okta': {
            'category': 'authentication',
            'criticality': 'critical',
            'business_processes': ['sso', 'user_management'],
            'rpm': 250,
            'customers_affected': 80000
        }
    }
    
    vendors = []
    vendor_counter = 1
    service_counter = 1
    
    # Process discovered vendors - deduplicate by normalizing names (case-insensitive)
    discovered_vendors = discovery_results.get('vendors', [])
    
    # Normalize vendor names and deduplicate
    # Use a dictionary to track normalized names and merge resources
    normalized_vendors = {}
    vendor_name_mapping = {}  # Maps normalized -> canonical name
    
    for vendor_info in discovered_vendors:
        vendor_name = vendor_info.get('name', 'Unknown')
        # Normalize: lowercase for comparison, but keep original casing for display
        normalized_name = vendor_name.lower().strip()
        
        # Find canonical name (prefer exact match in metadata, or first occurrence)
        canonical_name = vendor_name
        if normalized_name in normalized_vendors:
            # Use existing canonical name
            canonical_name = vendor_name_mapping.get(normalized_name, vendor_name)
        else:
            # Check if we have metadata for this vendor (case-insensitive)
            for known_vendor in vendor_metadata.keys():
                if known_vendor.lower() == normalized_name:
                    canonical_name = known_vendor
                    break
            vendor_name_mapping[normalized_name] = canonical_name
        
        # Merge resources if vendor already exists
        if normalized_name in normalized_vendors:
            existing_vendor = normalized_vendors[normalized_name]
            existing_resources = existing_vendor.get('resources', [])
            new_resources = vendor_info.get('resources', [])
            # Merge resources, avoiding duplicates
            existing_resource_names = {r.get('resource_name') for r in existing_resources}
            for resource in new_resources:
                if resource.get('resource_name') not in existing_resource_names:
                    existing_resources.append(resource)
        else:
            # Create new vendor entry
            normalized_vendors[normalized_name] = {
                'name': canonical_name,
                'resources': vendor_info.get('resources', []).copy()
            }
    
    # Process deduplicated vendors
    for normalized_name, vendor_data in normalized_vendors.items():
        vendor_name = vendor_data['name']
        metadata = vendor_metadata.get(vendor_name, {
            'category': 'unknown',
            'criticality': 'medium',
            'business_processes': ['general'],
            'rpm': 100,
            'customers_affected': 0
        })
        
        # Use normalized name for vendor_id to ensure uniqueness
        vendor_id = f"vendor_{normalized_name.replace(' ', '_').replace('-', '_')}"
        
        # Group resources by vendor
        resources = vendor_data.get('resources', [])
        
        # Create services from resources - deduplicate by GCP resource path
        services = []
        seen_gcp_resources = {}  # Track services by GCP resource to avoid duplicates
        
        for resource in resources:
            resource_name = resource.get('resource_name', 'unknown')
            resource_type = resource.get('resource_type', 'unknown')
            
            # Extract just the service name from full path if needed
            # Cloud Run names come as full paths: "projects/.../services/service-name"
            if resource_type == 'cloud_run' and '/services/' in resource_name:
                service_name = resource_name.split('/services/')[-1]
            elif resource_type == 'cloud_function' and '/functions/' in resource_name:
                service_name = resource_name.split('/functions/')[-1]
            else:
                service_name = resource_name
            
            # Extract GCP resource path (this is the unique identifier)
            if resource_type == 'cloud_function':
                gcp_resource = f"projects/{project_id}/locations/{discovery_results.get('region', 'us-central1')}/functions/{service_name}"
            elif resource_type == 'cloud_run':
                gcp_resource = f"projects/{project_id}/locations/{discovery_results.get('region', 'us-central1')}/services/{service_name}"
            else:
                gcp_resource = f"projects/{project_id}/resources/{service_name}"
            
            # Check if we've already seen this GCP resource
            if gcp_resource in seen_gcp_resources:
                # Reuse existing service_id for this GCP resource
                service_id = seen_gcp_resources[gcp_resource]
                logger.debug(f"Reusing service_id {service_id} for existing GCP resource: {gcp_resource}")
            else:
                # Create new service_id for this unique GCP resource
                service_id = f"svc_{service_counter:03d}"
                service_counter += 1
                seen_gcp_resources[gcp_resource] = service_id
            
            # Get environment variables from discovery
            env_vars = []
            if resource_type == 'cloud_function':
                # Find matching function in discovery results
                for func in discovery_results.get('cloud_functions', []):
                    func_name = func.get('name', '')
                    if func_name.endswith(service_name) or func_name.endswith(resource_name):
                        env_vars = list(func.get('environment_variables', {}).keys())
                        break
            elif resource_type == 'cloud_run':
                # Find matching service in discovery results
                for svc in discovery_results.get('cloud_run_services', []):
                    svc_name = svc.get('name', '')
                    if svc_name.endswith(service_name) or svc_name.endswith(resource_name) or service_name in svc_name:
                        env_vars = list(svc.get('environment_variables', {}).keys())
                        break
            
            service = {
                'service_id': service_id,
                'name': service_name,  # Use extracted service name, not full path
                'type': resource_type,
                'gcp_resource': gcp_resource,
                'environment_variables': env_vars,
                'business_processes': metadata['business_processes'],
                'rpm': metadata['rpm'],
                'customers_affected': metadata['customers_affected']
            }
            services.append(service)
        
        # If no resources found, create a placeholder service
        if not services:
            service_id = f"svc_{service_counter:03d}"
            service_counter += 1
            services.append({
                'service_id': service_id,
                'name': f"{vendor_name.lower()}-service",
                'type': 'unknown',
                'gcp_resource': f"projects/{project_id}/resources/{vendor_name.lower()}-service",
                'environment_variables': [],
                'business_processes': metadata['business_processes'],
                'rpm': metadata['rpm'],
                'customers_affected': metadata['customers_affected']
            })
        
        vendor = {
            'vendor_id': vendor_id,
            'name': vendor_name,
            'category': metadata['category'],
            'criticality': metadata['criticality'],
            'services': services
        }
        vendors.append(vendor)
    
    # Count services by type from the converted data
    cloud_functions_count = sum(
        1 for v in vendors 
        for s in v.get('services', []) 
        if s.get('type') == 'cloud_function'
    )
    cloud_run_services_count = sum(
        1 for v in vendors 
        for s in v.get('services', []) 
        if s.get('type') == 'cloud_run'
    )
    
    # Also try to get counts from original discovery results if available
    original_cf_count = len(discovery_results.get('cloud_functions', []))
    original_cr_count = len(discovery_results.get('cloud_run_services', []))
    
    result = {
        'vendors': vendors,
        'discovery_metadata': {
            'discovery_timestamp': discovery_results.get('discovery_timestamp'),
            'project_id': project_id,
            'source': 'gcp_discovery',
            'cloud_functions_count': cloud_functions_count or original_cf_count,
            'cloud_run_services_count': cloud_run_services_count or original_cr_count
        }
    }
    
    logger.info(f"✅ Converted {len(vendors)} vendors with {sum(len(v['services']) for v in vendors)} services")
    return result


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Fetch discovery results from Cloud Storage and convert to Neo4j format'
    )
    parser.add_argument(
        '--project-id',
        help='GCP project ID (defaults to GCP_PROJECT_ID env var)',
        default=os.getenv('GCP_PROJECT_ID')
    )
    parser.add_argument(
        '--bucket',
        help='Cloud Storage bucket name (defaults to {project-id}-discovery-results)',
        default=None
    )
    parser.add_argument(
        '--output-file',
        help='Output file path (defaults to data/outputs/discovery_neo4j.json)',
        default='data/outputs/discovery_neo4j.json'
    )
    parser.add_argument(
        '--load-to-neo4j',
        action='store_true',
        help='Automatically load results into Neo4j after conversion'
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
    
    # Validate project ID
    if not args.project_id:
        logger.error("--project-id is required or set GCP_PROJECT_ID environment variable")
        return 1
    
    # Fetch discovery results
    logger.info(f"Fetching latest discovery results for project: {args.project_id}")
    discovery_results = get_latest_discovery(args.project_id, args.bucket)
    
    if not discovery_results:
        logger.error("Failed to fetch discovery results")
        return 1
    
    # Convert to Neo4j format
    neo4j_data = convert_to_neo4j_format(discovery_results, args.project_id)
    
    # Save to file
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(neo4j_data, f, indent=2)
    
    logger.info(f"✅ Saved Neo4j-formatted data to: {output_path}")
    
    # Optionally load to Neo4j
    if args.load_to_neo4j:
        logger.info("Loading data into Neo4j...")
        try:
            from scripts.neo4j.load_graph import Neo4jGraphLoader
            from scripts.utils import load_config, validate_env_vars
            
            # Validate environment
            required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
            if not validate_env_vars(required_vars):
                logger.error("Neo4j credentials not configured. Skipping Neo4j load.")
                return 1
            
            config = load_config()
            neo4j_config = config['neo4j']
            
            loader = Neo4jGraphLoader(
                uri=neo4j_config['uri'],
                user=neo4j_config['user'],
                password=neo4j_config['password']
            )
            
            try:
                loader.load_dependencies(neo4j_data)
                stats = loader.verify_graph()
                logger.info("✅ Data loaded into Neo4j successfully!")
                logger.info(f"   - Vendors: {stats['Vendor_count']}")
                logger.info(f"   - Services: {stats['Service_count']}")
                logger.info(f"   - Business Processes: {stats['BusinessProcess_count']}")
                logger.info(f"   - Relationships: {stats['relationship_count']}")
            finally:
                loader.close()
        except Exception as e:
            logger.error(f"Failed to load into Neo4j: {e}", exc_info=True)
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

