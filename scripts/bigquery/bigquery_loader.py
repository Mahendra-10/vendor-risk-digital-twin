"""
BigQuery Data Loader for Vendor Risk Digital Twin

Loads simulation results and vendor dependencies into BigQuery for analytics.

Usage:
    # Load simulation results
    python scripts/bigquery/bigquery_loader.py --type simulation --data-file data/outputs/simulation_result.json
    
    # Load discovery results
    python scripts/bigquery/bigquery_loader.py --type dependencies --data-file data/outputs/discovered_dependencies.json
"""

import argparse
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.utils import (
    setup_logging,
    load_config,
    load_json_file,
)


def load_simulation_results(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    simulation_data: Dict[str, Any]
) -> int:
    """
    Load simulation results into BigQuery
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID
        simulation_data: Simulation result dictionary
    
    Returns:
        Number of rows inserted
    """
    table_id = f"{project_id}.{dataset_id}.simulations"
    
    # Generate unique simulation ID if not present
    simulation_id = simulation_data.get('simulation_id', f"sim_{uuid.uuid4().hex[:12]}")
    
    # Parse timestamp
    timestamp_str = simulation_data.get('timestamp', datetime.utcnow().isoformat())
    if isinstance(timestamp_str, str):
        # Parse and convert to ISO format string for BigQuery
        try:
            timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            timestamp = timestamp_dt.isoformat()
        except (ValueError, AttributeError):
            timestamp = datetime.utcnow().isoformat()
    else:
        timestamp = datetime.utcnow().isoformat()
    
    # Extract impact scores
    operational = simulation_data.get('operational_impact', {})
    financial = simulation_data.get('financial_impact', {})
    compliance = simulation_data.get('compliance_impact', {})
    
    row = {
        'simulation_id': simulation_id,
        'vendor_name': simulation_data.get('vendor', 'Unknown'),
        'duration_hours': simulation_data.get('duration_hours', 0),
        'operational_impact': operational.get('impact_score', 0.0),
        'financial_impact': financial.get('impact_score', 0.0),
        'compliance_impact': compliance.get('impact_score', 0.0),
        'overall_score': simulation_data.get('overall_impact_score', 0.0),
        'services_affected': operational.get('service_count', 0),
        'customers_affected': operational.get('customers_affected', 0),
        'revenue_loss': financial.get('revenue_loss', 0.0),
        'total_cost': financial.get('total_cost', 0.0),
        'timestamp': timestamp,  # ISO format string
        'created_at': datetime.utcnow().isoformat(),  # ISO format string
    }
    
    # Insert row
    errors = client.insert_rows_json(table_id, [row])
    
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")
    
    logging.info(f"✅ Loaded simulation result: {simulation_id} for vendor {row['vendor_name']}")
    return 1


def load_dependencies(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    discovery_data: Dict[str, Any]
) -> int:
    """
    Load vendor dependencies from discovery results into BigQuery
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID
        discovery_data: Discovery result dictionary
    
    Returns:
        Number of rows inserted
    """
    table_id = f"{project_id}.{dataset_id}.dependencies"
    
    rows = []
    discovered_at = datetime.utcnow().isoformat()  # ISO format string for BigQuery
    source_project_id = discovery_data.get('project_id', project_id)
    
    # Process vendors and their dependencies
    vendors = discovery_data.get('vendors', [])
    
    for vendor in vendors:
        vendor_name = vendor.get('name', 'Unknown')
        dependencies = vendor.get('dependencies', [])
        
        for dep in dependencies:
            row = {
                'vendor_name': vendor_name,
                'service_name': dep.get('service_name', 'Unknown'),
                'resource_type': dep.get('resource_type', 'unknown'),
                'resource_name': dep.get('resource_name', ''),
                'env_variable': dep.get('env_variable'),
                'project_id': source_project_id,
                'discovered_at': discovered_at,
            }
            rows.append(row)
    
    if not rows:
        logging.warning("No dependencies found in discovery data")
        return 0
    
    # Insert rows in batches
    errors = client.insert_rows_json(table_id, rows)
    
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")
    
    logging.info(f"✅ Loaded {len(rows)} dependency records for {len(vendors)} vendors")
    return len(rows)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Load data into BigQuery for Vendor Risk Digital Twin'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=['simulation', 'dependencies'],
        help='Type of data to load'
    )
    parser.add_argument(
        '--data-file',
        required=True,
        help='Path to JSON data file'
    )
    parser.add_argument(
        '--project-id',
        help='GCP Project ID (default: from config or env)'
    )
    parser.add_argument(
        '--dataset-id',
        default='vendor_risk',
        help='BigQuery Dataset ID (default: vendor_risk)'
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
    
    try:
        # Load config
        config = load_config()
        
        # Get project ID
        project_id = args.project_id or config.get('gcp', {}).get('project_id')
        if not project_id:
            # Try environment variable
            import os
            project_id = os.getenv('GCP_PROJECT_ID')
        
        if not project_id:
            logger.error("Project ID required. Set --project-id or GCP_PROJECT_ID env var")
            return 1
        
        # Initialize BigQuery client
        client = bigquery.Client(project=project_id)
        logger.info(f"📊 Loading {args.type} data into BigQuery...")
        logger.info(f"   Project: {project_id}")
        logger.info(f"   Dataset: {args.dataset_id}")
        logger.info(f"   File: {args.data_file}")
        
        # Load data file
        data = load_json_file(args.data_file)
        
        # Load based on type
        if args.type == 'simulation':
            rows_loaded = load_simulation_results(client, project_id, args.dataset_id, data)
        elif args.type == 'dependencies':
            rows_loaded = load_dependencies(client, project_id, args.dataset_id, data)
        
        logger.info("\n" + "="*60)
        logger.info(f"✅ Successfully loaded {rows_loaded} row(s) into BigQuery")
        logger.info("="*60 + "\n")
        
        return 0
    
    except FileNotFoundError:
        logger.error(f"Data file not found: {args.data_file}")
        return 1
    except Exception as e:
        logger.error(f"BigQuery load failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

