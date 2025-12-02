#!/usr/bin/env python3
"""
Quick script to check what GCP resources actually exist
"""

import sys
from pathlib import Path
from google.cloud import functions_v1, run_v2
from google.auth import default
import os

sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils import load_config, setup_logging

def check_resources():
    """Check what resources exist in GCP"""
    logger = setup_logging("INFO")
    
    config = load_config()
    project_id = config.get('gcp', {}).get('project_id') or os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not configured")
        return
    
    logger.info(f"Checking resources in project: {project_id}")
    
    # Check Cloud Functions
    try:
        functions_client = functions_v1.CloudFunctionsServiceClient()
        parent = f"projects/{project_id}/locations/-"
        request = functions_v1.ListFunctionsRequest(parent=parent)
        
        functions = list(functions_client.list_functions(request=request))
        logger.info(f"✅ Cloud Functions found: {len(functions)}")
        for func in functions:
            logger.info(f"   - {func.name}")
    except Exception as e:
        logger.warning(f"❌ Error checking Cloud Functions: {e}")
        logger.info("   (This might mean you don't have any, or API permissions are missing)")
    
    # Check Cloud Run
    try:
        run_client = run_v2.ServicesClient()
        parent = f"projects/{project_id}/locations/-"
        request = run_v2.ListServicesRequest(parent=parent)
        
        services = list(run_client.list_services(request=request))
        logger.info(f"✅ Cloud Run services found: {len(services)}")
        for svc in services:
            logger.info(f"   - {svc.name}")
    except Exception as e:
        logger.warning(f"❌ Error checking Cloud Run: {e}")

if __name__ == "__main__":
    check_resources()
