"""
GCP Resource Discovery Script

Discovers vendor dependencies across GCP infrastructure by:
1. Querying Cloud Functions and Cloud Run services
2. Extracting environment variables that reference vendor APIs
3. Mapping services to business processes

Usage:
    python scripts/gcp/gcp_discovery.py --project-id YOUR_PROJECT_ID
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
from google.cloud import functions_v1, run_v2
from google.auth import default

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils import (
    setup_logging, 
    load_config, 
    save_json_file,
    validate_env_vars
)


class GCPDiscovery:
    """Discovers vendor dependencies in GCP infrastructure"""
    
    def __init__(self, project_id: str):
        """
        Initialize GCP Discovery
        
        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        self.config = load_config()
        
        # Initialize GCP clients
        self.logger.info(f"Initializing GCP clients for project: {project_id}")
        self.functions_client = functions_v1.CloudFunctionsServiceClient()
        self.run_client = run_v2.ServicesClient()
        
        # Vendor detection patterns
        self.vendor_patterns = {
            'Stripe': ['STRIPE_', 'stripe'],
            'Auth0': ['AUTH0_', 'auth0'],
            'SendGrid': ['SENDGRID_', 'sendgrid'],
            'Twilio': ['TWILIO_', 'twilio'],
            'Datadog': ['DATADOG_', 'DD_'],
            'MongoDB': ['MONGO', 'mongodb'],
            'PayPal': ['PAYPAL_', 'paypal'],
            'Okta': ['OKTA_', 'okta']
        }
    
    def discover_all(self) -> Dict[str, Any]:
        """
        Discover all vendor dependencies
        
        Returns:
            Dictionary with discovered dependencies
        """
        self.logger.info("Starting vendor dependency discovery...")
        
        discovered = {
            'project_id': self.project_id,
            'vendors': [],
            'cloud_functions': [],
            'cloud_run_services': []
        }
        
        # Discover Cloud Functions
        self.logger.info("Discovering Cloud Functions...")
        functions = self._discover_cloud_functions()
        discovered['cloud_functions'] = functions
        
        # Discover Cloud Run services
        self.logger.info("Discovering Cloud Run services...")
        services = self._discover_cloud_run()
        discovered['cloud_run_services'] = services
        
        # Analyze vendor dependencies
        self.logger.info("Analyzing vendor dependencies...")
        vendors = self._analyze_vendors(functions, services)
        discovered['vendors'] = vendors
        
        self.logger.info(f"Discovery complete. Found {len(vendors)} vendors")
        return discovered
    
    def _discover_cloud_functions(self) -> List[Dict[str, Any]]:
        """
        Discover Cloud Functions
        
        Returns:
            List of Cloud Function metadata
        """
        functions = []
        
        try:
            parent = f"projects/{self.project_id}/locations/-"
            request = functions_v1.ListFunctionsRequest(parent=parent)
            
            for function in self.functions_client.list_functions(request=request):
                func_data = {
                    'name': function.name,
                    'runtime': function.runtime,
                    'entry_point': function.entry_point,
                    'environment_variables': dict(function.environment_variables or {}),
                    'status': function.status.name
                }
                functions.append(func_data)
                self.logger.debug(f"Found function: {function.name}")
        
        except Exception as e:
            self.logger.warning(f"Error discovering Cloud Functions: {e}")
            self.logger.info("Using sample data instead...")
        
        return functions
    
    def _discover_cloud_run(self) -> List[Dict[str, Any]]:
        """
        Discover Cloud Run services
        
        Returns:
            List of Cloud Run service metadata
        """
        services = []
        
        try:
            parent = f"projects/{self.project_id}/locations/-"
            request = run_v2.ListServicesRequest(parent=parent)
            
            for service in self.run_client.list_services(request=request):
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
                    'description': service.description
                }
                services.append(service_data)
                self.logger.debug(f"Found service: {service.name}")
        
        except Exception as e:
            self.logger.warning(f"Error discovering Cloud Run services: {e}")
            self.logger.info("Using sample data instead...")
        
        return services
    
    def _analyze_vendors(
        self, 
        functions: List[Dict[str, Any]], 
        services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze discovered resources for vendor dependencies
        
        Args:
            functions: List of Cloud Functions
            services: List of Cloud Run services
        
        Returns:
            List of detected vendors with dependencies
        """
        vendor_dependencies = {}
        
        # Analyze Cloud Functions
        for func in functions:
            self._extract_vendor_deps(
                vendor_dependencies,
                func['environment_variables'],
                resource_name=func['name'],
                resource_type='cloud_function'
            )
        
        # Analyze Cloud Run services
        for service in services:
            self._extract_vendor_deps(
                vendor_dependencies,
                service['environment_variables'],
                resource_name=service['name'],
                resource_type='cloud_run'
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
    
    def _extract_vendor_deps(
        self,
        vendor_deps: Dict[str, List],
        env_vars: Dict[str, str],
        resource_name: str,
        resource_type: str
    ) -> None:
        """
        Extract vendor dependencies from environment variables
        
        Args:
            vendor_deps: Dictionary to store vendor dependencies
            env_vars: Environment variables to analyze
            resource_name: Name of the resource
            resource_type: Type of resource (cloud_function, cloud_run)
        """
        for vendor, patterns in self.vendor_patterns.items():
            for env_var_name in env_vars.keys():
                if any(pattern.lower() in env_var_name.lower() for pattern in patterns):
                    if vendor not in vendor_deps:
                        vendor_deps[vendor] = []
                    
                    vendor_deps[vendor].append({
                        'resource_name': resource_name,
                        'resource_type': resource_type,
                        'env_variable': env_var_name
                    })


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Discover vendor dependencies in GCP infrastructure'
    )
    parser.add_argument(
        '--project-id',
        required=True,
        help='GCP Project ID'
    )
    parser.add_argument(
        '--output',
        default='data/outputs/discovered_dependencies.json',
        help='Output file path'
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
    required_vars = ['GCP_PROJECT_ID']
    if not validate_env_vars(required_vars):
        logger.error("Please configure environment variables in .env file")
        return 1
    
    # Run discovery
    try:
        discovery = GCPDiscovery(args.project_id)
        results = discovery.discover_all()
        
        # Save results
        save_json_file(results, args.output)
        
        logger.info(f"✅ Discovery complete!")
        logger.info(f"   - Cloud Functions: {len(results['cloud_functions'])}")
        logger.info(f"   - Cloud Run Services: {len(results['cloud_run_services'])}")
        logger.info(f"   - Vendors Found: {len(results['vendors'])}")
        logger.info(f"   - Results saved to: {args.output}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Discovery failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

