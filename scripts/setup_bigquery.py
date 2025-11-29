"""
Setup BigQuery Dataset and Tables for Vendor Risk Digital Twin

Creates the necessary BigQuery dataset and tables for storing:
- Simulation results
- Vendor dependencies
- Historical analytics

Usage:
    python scripts/setup_bigquery.py --project-id vendor-risk-digital-twin
"""

import argparse
import logging
import sys
from pathlib import Path
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils import setup_logging


def create_dataset(client: bigquery.Client, project_id: str, dataset_id: str) -> bigquery.Dataset:
    """
    Create BigQuery dataset if it doesn't exist
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID (e.g., 'vendor_risk')
    
    Returns:
        Created or existing dataset
    """
    dataset_ref = client.dataset(dataset_id, project=project_id)
    
    try:
        dataset = client.get_dataset(dataset_ref)
        logging.info(f"✅ Dataset '{dataset_id}' already exists")
        return dataset
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.description = "Vendor Risk Digital Twin Analytics Dataset"
        dataset.location = "US"  # Multi-region US
        
        dataset = client.create_dataset(dataset, exists_ok=False)
        logging.info(f"✅ Created dataset '{dataset_id}'")
        return dataset


def create_simulations_table(client: bigquery.Client, project_id: str, dataset_id: str) -> bigquery.Table:
    """
    Create simulations results table
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID
    
    Returns:
        Created or existing table
    """
    table_id = f"{project_id}.{dataset_id}.simulations"
    table_ref = client.dataset(dataset_id, project=project_id).table("simulations")
    
    try:
        table = client.get_table(table_ref)
        logging.info(f"✅ Table 'simulations' already exists")
        return table
    except NotFound:
        schema = [
            bigquery.SchemaField("simulation_id", "STRING", mode="REQUIRED", description="Unique simulation ID"),
            bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED", description="Vendor name"),
            bigquery.SchemaField("duration_hours", "INTEGER", mode="REQUIRED", description="Failure duration in hours"),
            bigquery.SchemaField("operational_impact", "FLOAT", mode="NULLABLE", description="Operational impact score (0-1)"),
            bigquery.SchemaField("financial_impact", "FLOAT", mode="NULLABLE", description="Financial impact score (0-1)"),
            bigquery.SchemaField("compliance_impact", "FLOAT", mode="NULLABLE", description="Compliance impact score (0-1)"),
            bigquery.SchemaField("overall_score", "FLOAT", mode="REQUIRED", description="Overall impact score (0-1)"),
            bigquery.SchemaField("services_affected", "INTEGER", mode="NULLABLE", description="Number of services affected"),
            bigquery.SchemaField("customers_affected", "INTEGER", mode="NULLABLE", description="Number of customers affected"),
            bigquery.SchemaField("revenue_loss", "FLOAT", mode="NULLABLE", description="Estimated revenue loss in USD"),
            bigquery.SchemaField("total_cost", "FLOAT", mode="NULLABLE", description="Total estimated cost in USD"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED", description="Simulation timestamp"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Record creation timestamp"),
        ]
        
        table = bigquery.Table(table_ref, schema=schema)
        table.description = "Vendor failure simulation results"
        
        table = client.create_table(table, exists_ok=False)
        logging.info(f"✅ Created table 'simulations'")
        return table


def create_dependencies_table(client: bigquery.Client, project_id: str, dataset_id: str) -> bigquery.Table:
    """
    Create vendor dependencies table
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID
    
    Returns:
        Created or existing table
    """
    table_id = f"{project_id}.{dataset_id}.dependencies"
    table_ref = client.dataset(dataset_id, project=project_id).table("dependencies")
    
    try:
        table = client.get_table(table_ref)
        logging.info(f"✅ Table 'dependencies' already exists")
        return table
    except NotFound:
        schema = [
            bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED", description="Vendor name"),
            bigquery.SchemaField("service_name", "STRING", mode="REQUIRED", description="Service name"),
            bigquery.SchemaField("resource_type", "STRING", mode="REQUIRED", description="Resource type (cloud_function, cloud_run)"),
            bigquery.SchemaField("resource_name", "STRING", mode="REQUIRED", description="Full GCP resource name"),
            bigquery.SchemaField("env_variable", "STRING", mode="NULLABLE", description="Environment variable that detected vendor"),
            bigquery.SchemaField("project_id", "STRING", mode="REQUIRED", description="GCP project ID"),
            bigquery.SchemaField("discovered_at", "TIMESTAMP", mode="REQUIRED", description="Discovery timestamp"),
        ]
        
        table = bigquery.Table(table_ref, schema=schema)
        table.description = "Vendor dependencies discovered from GCP resources"
        
        table = client.create_table(table, exists_ok=False)
        logging.info(f"✅ Created table 'dependencies'")
        return table


def create_analytics_views(client: bigquery.Client, project_id: str, dataset_id: str) -> None:
    """
    Create analytics views for common queries
    
    Args:
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: Dataset ID
    """
    views = {
        "most_critical_vendors": """
            SELECT 
                vendor_name,
                COUNT(*) as simulation_count,
                AVG(overall_score) as avg_impact_score,
                MAX(overall_score) as max_impact_score,
                SUM(revenue_loss) as total_revenue_loss,
                MAX(timestamp) as last_simulated
            FROM `{project_id}.{dataset_id}.simulations`
            GROUP BY vendor_name
            ORDER BY avg_impact_score DESC
        """,
        "impact_trends": """
            SELECT 
                DATE(timestamp) as simulation_date,
                vendor_name,
                AVG(overall_score) as avg_score,
                AVG(revenue_loss) as avg_revenue_loss,
                COUNT(*) as simulation_count
            FROM `{project_id}.{dataset_id}.simulations`
            GROUP BY simulation_date, vendor_name
            ORDER BY simulation_date DESC, avg_score DESC
        """,
        "vendor_dependency_summary": """
            SELECT 
                vendor_name,
                COUNT(DISTINCT service_name) as unique_services,
                COUNT(*) as total_dependencies,
                STRING_AGG(DISTINCT resource_type) as resource_types,
                MAX(discovered_at) as last_discovered
            FROM `{project_id}.{dataset_id}.dependencies`
            GROUP BY vendor_name
            ORDER BY total_dependencies DESC
        """
    }
    
    for view_name, query in views.items():
        view_ref = client.dataset(dataset_id, project=project_id).table(view_name)
        
        try:
            view = client.get_table(view_ref)
            logging.info(f"✅ View '{view_name}' already exists")
        except NotFound:
            view = bigquery.Table(view_ref)
            view.view_query = query.format(project_id=project_id, dataset_id=dataset_id)
            view.description = f"Analytics view: {view_name.replace('_', ' ').title()}"
            
            view = client.create_table(view, exists_ok=False)
            logging.info(f"✅ Created view '{view_name}'")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Setup BigQuery dataset and tables for Vendor Risk Digital Twin'
    )
    parser.add_argument(
        '--project-id',
        required=True,
        help='GCP Project ID'
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
        # Initialize BigQuery client
        client = bigquery.Client(project=args.project_id)
        logger.info(f"🔧 Setting up BigQuery for project: {args.project_id}")
        
        # Create dataset
        dataset = create_dataset(client, args.project_id, args.dataset_id)
        
        # Create tables
        create_simulations_table(client, args.project_id, args.dataset_id)
        create_dependencies_table(client, args.project_id, args.dataset_id)
        
        # Create analytics views
        logger.info("Creating analytics views...")
        create_analytics_views(client, args.project_id, args.dataset_id)
        
        logger.info("\n" + "="*60)
        logger.info("✅ BigQuery setup complete!")
        logger.info("="*60)
        logger.info(f"   Dataset: {args.project_id}.{args.dataset_id}")
        logger.info(f"   Tables: simulations, dependencies")
        logger.info(f"   Views: most_critical_vendors, impact_trends, vendor_dependency_summary")
        logger.info("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"BigQuery setup failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())

