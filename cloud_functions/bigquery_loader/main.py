"""
Cloud Function: BigQuery Loader (Pub/Sub Subscriber)

Subscribes to simulation-results and automatically loads simulation results into BigQuery.

Trigger: Pub/Sub topic 'simulation-results'
"""

import json
import logging
import os
import base64
import sys
from pathlib import Path
from typing import Dict, Any
from google.cloud import bigquery
import google.cloud.pubsub_v1 as pubsub_v1

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_simulation_to_bigquery(result: Dict[str, Any], project_id: str, dataset_id: str = 'vendor_risk') -> None:
    """
    Load simulation result into BigQuery
    
    Args:
        result: Simulation result dictionary
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
    """
    try:
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_id}.simulations"
        
        # Extract data
        simulation_id = result.get('simulation_id', f"sim_{result.get('vendor', 'unknown').lower()}")
        vendor_name = result.get('vendor', 'Unknown')
        duration_hours = result.get('duration_hours', 0)
        
        operational = result.get('operational_impact', {})
        financial = result.get('financial_impact', {})
        compliance = result.get('compliance_impact', {})
        
        # Parse timestamp
        timestamp_str = result.get('timestamp', '')
        if isinstance(timestamp_str, str):
            from datetime import datetime
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).isoformat()
            except:
                from datetime import datetime, timezone
                timestamp = datetime.now(timezone.utc).isoformat()
        else:
            from datetime import datetime, timezone
            timestamp = datetime.now(timezone.utc).isoformat()
        
        row = {
            'simulation_id': simulation_id,
            'vendor_name': vendor_name,
            'duration_hours': duration_hours,
            'operational_impact': operational.get('impact_score', 0.0),
            'financial_impact': financial.get('impact_score', 0.0),
            'compliance_impact': compliance.get('impact_score', 0.0),
            'overall_score': result.get('overall_impact_score', 0.0),
            'services_affected': operational.get('service_count', 0),
            'customers_affected': operational.get('customers_affected', 0),
            'revenue_loss': financial.get('revenue_loss', 0.0),
            'total_cost': financial.get('total_cost', 0.0),
            'timestamp': timestamp,
            'created_at': timestamp,  # Use same timestamp for created_at
        }
        
        # Insert row
        errors = client.insert_rows_json(table_id, [row])
        
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")
        
        logger.info(f"✅ Loaded simulation result into BigQuery: {simulation_id}")
        
    except Exception as e:
        logger.error(f"Failed to load into BigQuery: {e}", exc_info=True)
        raise


def load_simulation_result(event: Dict[str, Any], context) -> None:
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
        dataset_id = os.getenv('BIGQUERY_DATASET_ID', 'vendor_risk')
        
        if not project_id:
            raise ValueError("project_id not found in event or environment")
        
        # Get full result from event
        result = event_data.get('full_result', event_data)
        
        logger.info(f"📥 Received simulation result event")
        logger.info(f"   Simulation ID: {result.get('simulation_id')}")
        logger.info(f"   Vendor: {result.get('vendor')}")
        
        # Load into BigQuery
        load_simulation_to_bigquery(result, project_id, dataset_id)
        
        logger.info("✅ Simulation result successfully loaded into BigQuery")
        
    except Exception as e:
        logger.error(f"❌ Failed to load simulation to BigQuery: {e}", exc_info=True)
        # Re-raise to trigger Pub/Sub retry
        raise


# For local testing
if __name__ == "__main__":
    # Test with sample event
    test_result = {
        'simulation_id': 'test-sim-123',
        'vendor': 'Stripe',
        'duration_hours': 4,
        'overall_impact_score': 0.32,
        'operational_impact': {'impact_score': 0.3, 'service_count': 2, 'customers_affected': 50000},
        'financial_impact': {'impact_score': 0.35, 'revenue_loss': 300000, 'total_cost': 550000},
        'compliance_impact': {'impact_score': 0.25},
        'timestamp': '2025-11-27T20:00:00Z'
    }
    
    test_event = {
        'data': base64.b64encode(json.dumps({
            'project_id': os.getenv('GCP_PROJECT_ID', 'vendor-risk-digital-twin'),
            'full_result': test_result
        }).encode('utf-8')).decode('utf-8')
    }
    load_simulation_result(test_event, None)

