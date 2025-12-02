"""
Cloud Function: Vendor Discovery

Discovers vendor dependencies across GCP infrastructure and stores results in Cloud Storage.

Supports:
- HTTP triggers (manual invocation)
- Pub/Sub triggers (scheduled scans)
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
from google.cloud import storage
from google.cloud import functions_v1, run_v2
from google.cloud import pubsub_v1

# Configure logging for Cloud Functions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Vendor detection patterns
VENDOR_PATTERNS = {
    'Stripe': ['STRIPE_', 'stripe'],
    'Auth0': ['AUTH0_', 'auth0'],
    'SendGrid': ['SENDGRID_', 'sendgrid'],
    'Twilio': ['TWILIO_', 'twilio'],
    'Datadog': ['DATADOG_', 'DD_'],
    'MongoDB': ['MONGO', 'mongodb'],
    'PayPal': ['PAYPAL_', 'paypal'],
    'Okta': ['OKTA_', 'okta']
}


def discover_vendors(request):
    """
    Cloud Function entry point for HTTP triggers
    
    Args:
        request: Flask request object (for HTTP triggers)
    
    Returns:
        HTTP response with discovery results
    """
    try:
        # Get project ID from environment or request
        project_id = os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        
        if not project_id:
            # Try to get from request
            if hasattr(request, 'args'):
                project_id = request.args.get('project_id')
            if not project_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'GCP_PROJECT_ID or project_id parameter required'})
                }
        
        logger.info(f"Starting vendor discovery for project: {project_id}")
        
        # Run discovery
        results = run_discovery(project_id)
        
        # Store results in Cloud Storage
        storage_path = store_results(results, project_id)
        
        # Publish event to Pub/Sub
        publish_discovery_event(project_id, storage_path, results)
        
        # Return response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'project_id': project_id,
                'discovery_timestamp': results.get('discovery_timestamp'),
                'summary': {
                    'cloud_functions': len(results.get('cloud_functions', [])),
                    'cloud_run_services': len(results.get('cloud_run_services', [])),
                    'vendors_found': len(results.get('vendors', []))
                },
                'storage_path': storage_path
            })
        }
        
        logger.info(f"Discovery complete. Results stored at: {storage_path}")
        return response
    
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def discover_vendors_pubsub(event, context):
    """
    Cloud Function entry point for Pub/Sub triggers
    
    Args:
        event: Pub/Sub event
        context: Function context
    
    Returns:
        None (results stored in Cloud Storage)
    """
    try:
        # Get project ID from environment
        project_id = os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        
        if not project_id:
            logger.error("GCP_PROJECT_ID not set")
            return
        
        # Get project from Pub/Sub message if provided
        if event and 'data' in event:
            import base64
            message_data = base64.b64decode(event['data']).decode('utf-8')
            message_json = json.loads(message_data)
            if 'project_id' in message_json:
                project_id = message_json['project_id']
        
        logger.info(f"Starting scheduled vendor discovery for project: {project_id}")
        
        # Run discovery
        results = run_discovery(project_id)
        
        # Store results in Cloud Storage
        storage_path = store_results(results, project_id)
        
        # Publish event to Pub/Sub
        publish_discovery_event(project_id, storage_path, results)
        
        logger.info(f"Scheduled discovery complete. Results stored at: {storage_path}")
        
    except Exception as e:
        logger.error(f"Scheduled discovery failed: {e}", exc_info=True)
        raise


def run_discovery(project_id: str) -> Dict[str, Any]:
    """
    Run vendor dependency discovery
    
    Args:
        project_id: GCP project ID
    
    Returns:
        Dictionary with discovery results
    """
    logger.info(f"Discovering vendor dependencies for project: {project_id}")
    
    results = {
        'project_id': project_id,
        'discovery_timestamp': datetime.utcnow().isoformat(),
        'vendors': [],
        'cloud_functions': [],
        'cloud_run_services': []
    }
    
    # Initialize GCP clients
    functions_client = functions_v1.CloudFunctionsServiceClient()
    run_client = run_v2.ServicesClient()
    
    # Discover Cloud Functions
    logger.info("Discovering Cloud Functions...")
    functions = discover_cloud_functions(functions_client, project_id)
    results['cloud_functions'] = functions
    
    # Discover Cloud Run services
    logger.info("Discovering Cloud Run services...")
    services = discover_cloud_run(run_client, project_id)
    results['cloud_run_services'] = services
    
    # Analyze vendor dependencies
    logger.info("Analyzing vendor dependencies...")
    vendors = analyze_vendors(functions, services)
    results['vendors'] = vendors
    
    logger.info(f"Discovery complete. Found {len(vendors)} vendors")
    return results


def discover_cloud_functions(client: functions_v1.CloudFunctionsServiceClient, project_id: str) -> list:
    """Discover Cloud Functions"""
    functions = []
    
    try:
        parent = f"projects/{project_id}/locations/-"
        request = functions_v1.ListFunctionsRequest(parent=parent)
        
        for function in client.list_functions(request=request):
            func_data = {
                'name': function.name,
                'runtime': function.runtime,
                'entry_point': function.entry_point,
                'environment_variables': dict(function.environment_variables or {}),
                'status': function.status.name if function.status else 'UNKNOWN'
            }
            functions.append(func_data)
            logger.debug(f"Found function: {function.name}")
    
    except Exception as e:
        logger.warning(f"Error discovering Cloud Functions: {e}")
    
    return functions


def discover_cloud_run(client: run_v2.ServicesClient, project_id: str) -> list:
    """Discover Cloud Run services"""
    services = []
    
    try:
        parent = f"projects/{project_id}/locations/-"
        request = run_v2.ListServicesRequest(parent=parent)
        
        for service in client.list_services(request=request):
            # Extract environment variables from containers
            env_vars = {}
            if service.template and service.template.containers:
                for container in service.template.containers:
                    for env in container.env:
                        env_vars[env.name] = env.value or ""
            
            service_data = {
                'name': service.name,
                'uri': service.uri,
                'environment_variables': env_vars,
                'description': service.description or ""
            }
            services.append(service_data)
            logger.debug(f"Found service: {service.name}")
    
    except Exception as e:
        logger.warning(f"Error discovering Cloud Run services: {e}")
    
    return services


def analyze_vendors(functions: list, services: list) -> list:
    """Analyze discovered resources for vendor dependencies"""
    vendor_dependencies = {}
    
    # Analyze Cloud Functions
    for func in functions:
        extract_vendor_deps(
            vendor_dependencies,
            func.get('environment_variables', {}),
            func.get('name', ''),
            'cloud_function'
        )
    
    # Analyze Cloud Run services
    for service in services:
        extract_vendor_deps(
            vendor_dependencies,
            service.get('environment_variables', {}),
            service.get('name', ''),
            'cloud_run'
        )
    
    # Format vendor list
    vendors = []
    for vendor_name, deps in vendor_dependencies.items():
        vendors.append({
            'name': vendor_name,
            'dependency_count': len(deps),
            'resources': deps
        })
    
    return vendors


def extract_vendor_deps(vendor_deps: dict, env_vars: dict, resource_name: str, resource_type: str):
    """Extract vendor dependencies from environment variables"""
    for vendor, patterns in VENDOR_PATTERNS.items():
        for env_var_name in env_vars.keys():
            if any(pattern.lower() in env_var_name.lower() for pattern in patterns):
                if vendor not in vendor_deps:
                    vendor_deps[vendor] = []
                
                vendor_deps[vendor].append({
                    'resource_name': resource_name,
                    'resource_type': resource_type,
                    'env_variable': env_var_name
                })


def publish_discovery_event(project_id: str, storage_path: str, results: Dict[str, Any]) -> None:
    """
    Publish discovery completion event to Pub/Sub
    
    Args:
        project_id: GCP project ID
        storage_path: Path to results in Cloud Storage
        results: Discovery results
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, 'vendor-discovery-events')
        
        # Create event message
        event_data = {
            'project_id': project_id,
            'storage_path': storage_path,
            'discovery_timestamp': results.get('discovery_timestamp', datetime.utcnow().isoformat()),
            'summary': {
                'cloud_functions': len(results.get('cloud_functions', [])),
                'cloud_run_services': len(results.get('cloud_run_services', [])),
                'vendors_found': len(results.get('vendors', []))
            }
        }
        
        # Publish message
        message_data = json.dumps(event_data).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        logger.info(f"✅ Published discovery event to Pub/Sub: {message_id}")
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to publish discovery event: {e}")
        # Don't fail the discovery if publishing fails


def store_results(results: Dict[str, Any], project_id: str) -> str:
    """
    Store discovery results in Cloud Storage
    
    Args:
        results: Discovery results dictionary
        project_id: GCP project ID
    
    Returns:
        Cloud Storage path where results were stored
    """
    bucket_name = os.getenv('STORAGE_BUCKET', f'{project_id}-discovery-results')
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    blob_name = f'discoveries/{timestamp}_discovery.json'
    
    try:
        storage_client = storage.Client(project=project_id)
        
        # Get or create bucket
        try:
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                logger.info(f"Creating bucket: {bucket_name}")
                bucket = storage_client.create_bucket(bucket_name, location='us-central1')
        except Exception as e:
            logger.warning(f"Error accessing bucket {bucket_name}: {e}")
            # Try with default bucket name
            bucket_name = f'{project_id}-discovery-results'
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                bucket = storage_client.create_bucket(bucket_name, location='us-central1')
        
        # Upload results
        blob = bucket.blob(blob_name)
        blob.upload_from_string(
            json.dumps(results, indent=2),
            content_type='application/json'
        )
        
        storage_path = f'gs://{bucket_name}/{blob_name}'
        logger.info(f"Results stored in Cloud Storage: {storage_path}")
        return storage_path
    
    except Exception as e:
        logger.error(f"Failed to store results in Cloud Storage: {e}")
        # Return a local path indicator if storage fails
        return f'local://{blob_name}'

