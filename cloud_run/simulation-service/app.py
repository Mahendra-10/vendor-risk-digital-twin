"""
Cloud Run Service: Vendor Failure Simulation API

REST API for running vendor failure simulations.
Deployed as a containerized service on Google Cloud Run.

Endpoints:
    POST /simulate - Run a vendor failure simulation
    GET /simulate/{simulation_id} - Get simulation results (future)
    GET /health - Health check endpoint
    GET /vendors - List available vendors
"""

import os
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.cloud.pubsub_v1 as pubsub_v1

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import simulation module (updated path: scripts/simulation/simulate_failure.py)
from scripts.simulation.simulate_failure import VendorFailureSimulator
from scripts.utils import (
    setup_logging,
    load_config,
    validate_env_vars
)
from scripts.gcp.gcp_secrets import get_secret

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global simulator instance (initialized on first use)
simulator: Optional[VendorFailureSimulator] = None


def publish_simulation_result(result: Dict[str, Any]) -> None:
    """
    Publish simulation result event to Pub/Sub
    
    Args:
        result: Simulation result dictionary
    """
    try:
        project_id = os.getenv('GCP_PROJECT_ID')
        if not project_id:
            logger.warning("GCP_PROJECT_ID not set, skipping Pub/Sub publish")
            return
        
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, 'simulation-results')
        
        # Create event message (only essential data for BigQuery)
        event_data = {
            'simulation_id': result.get('simulation_id'),
            'vendor': result.get('vendor'),
            'duration_hours': result.get('duration_hours'),
            'overall_impact_score': result.get('overall_impact_score'),
            'operational_impact': result.get('operational_impact', {}).get('impact_score'),
            'financial_impact': result.get('financial_impact', {}).get('impact_score'),
            'compliance_impact': result.get('compliance_impact', {}).get('impact_score'),
            'timestamp': result.get('timestamp'),
            'full_result': result  # Include full result for BigQuery loader
        }
        
        # Publish message
        message_data = json.dumps(event_data).encode('utf-8')
        future = publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        logger.info(f"✅ Published simulation result to Pub/Sub: {message_id}")
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to publish simulation result: {e}")
        # Don't fail the simulation if publishing fails


def get_neo4j_credentials() -> Dict[str, str]:
    """
    Get Neo4j credentials from GCP Secret Manager or environment variables
    
    Returns:
        Dictionary with uri, user, and password
    """
    project_id = os.getenv('GCP_PROJECT_ID')
    
    # Try Secret Manager first
    if project_id:
        uri = get_secret('neo4j-uri', project_id) or os.getenv('NEO4J_URI')
        user = get_secret('neo4j-user', project_id) or os.getenv('NEO4J_USER', 'neo4j')
        password = get_secret('neo4j-password', project_id) or os.getenv('NEO4J_PASSWORD')
    else:
        # Fallback to environment variables
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
    
    if not uri or not password:
        raise ValueError("Neo4j credentials not configured. Set NEO4J_URI and NEO4J_PASSWORD or use GCP Secret Manager.")
    
    return {
        'uri': uri,
        'user': user,
        'password': password
    }


def init_simulator():
    """Initialize the simulator (lazy initialization)"""
    global simulator
    
    if simulator is None:
        try:
            credentials = get_neo4j_credentials()
            simulator = VendorFailureSimulator(
                neo4j_uri=credentials['uri'],
                neo4j_user=credentials['user'],
                neo4j_password=credentials['password']
            )
            logger.info("Simulator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize simulator: {e}", exc_info=True)
            raise
    
    return simulator


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try to initialize simulator if not already done
        sim = init_simulator()
        
        # Test Neo4j connection
        session = sim.driver.session()
        session.run('RETURN 1 as test')
        session.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'simulation-service',
            'neo4j': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'simulation-service',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/vendors', methods=['GET'])
def list_vendors():
    """List all available vendors from Neo4j"""
    try:
        sim = init_simulator()
        session = sim.driver.session()
        
        result = session.run('MATCH (v:Vendor) RETURN v.name as name ORDER BY v.name')
        vendors = [record['name'] for record in result]
        session.close()
        
        return jsonify({
            'vendors': vendors,
            'count': len(vendors)
        }), 200
    except Exception as e:
        logger.error(f"Failed to list vendors: {e}", exc_info=True)
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/simulate', methods=['POST'])
def run_simulation():
    """
    Run a vendor failure simulation
    
    Request Body:
        {
            "vendor": "Stripe",
            "duration": 4
        }
    
    Returns:
        Simulation results with impact analysis
    """
    try:
        # Parse request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        vendor = data.get('vendor')
        duration = data.get('duration', 4)
        
        if not vendor:
            return jsonify({'error': 'vendor field is required'}), 400
        
        if not isinstance(duration, (int, float)) or duration <= 0:
            return jsonify({'error': 'duration must be a positive number'}), 400
        
        duration_hours = int(duration)
        
        # Initialize simulator
        sim = init_simulator()
        
        # Run simulation
        # Note: vendor comes in as lowercase (normalized), but simulate_vendor_failure
        # will handle normalization and capitalization internally
        logger.info(f"Running simulation: {vendor} for {duration_hours} hours")
        result = sim.simulate_vendor_failure(vendor, duration_hours)
        
        # Add simulation metadata
        result['simulation_id'] = f"{vendor.lower()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        result['service'] = 'simulation-service'
        result['deployed_at'] = os.getenv('K_SERVICE', 'local')
        
        # Log compliance data for debugging
        compliance = result.get('compliance_impact', {})
        logger.info(f"Simulation complete. Impact score: {result['overall_impact_score']:.2f}")
        logger.info(f"Compliance frameworks: {len(compliance.get('affected_frameworks', {}))}")
        logger.info(f"Compliance summary: {len(compliance.get('summary', {}))}")
        
        # Publish event to Pub/Sub
        publish_simulation_result(result)
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        return jsonify({
            'error': 'Simulation failed',
            'message': str(e)
        }), 500


@app.route('/simulate/<simulation_id>', methods=['GET'])
def get_simulation(simulation_id: str):
    """
    Get simulation results by ID (placeholder for future implementation)
    
    For now, returns a message indicating this feature is not yet implemented.
    Future: Store results in Cloud Storage or Firestore and retrieve by ID.
    """
    return jsonify({
        'message': 'Simulation result retrieval not yet implemented',
        'simulation_id': simulation_id,
        'note': 'Results are returned immediately from POST /simulate endpoint'
    }), 501


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'Vendor Risk Digital Twin - Simulation Service',
        'version': '1.0.0',
        'endpoints': {
            'POST /simulate': 'Run a vendor failure simulation',
            'GET /simulate/{id}': 'Get simulation results (future)',
            'GET /vendors': 'List available vendors',
            'GET /health': 'Health check',
            'GET /': 'This endpoint'
        },
        'documentation': 'https://github.com/your-repo/vendor-risk-digital-twin'
    }), 200


if __name__ == '__main__':
    # Get port from environment (Cloud Run sets PORT automatically)
    port = int(os.environ.get('PORT', 8080))
    
    # Don't initialize simulator on startup - use lazy initialization
    # This prevents startup failures if Neo4j is temporarily unavailable
    logger.info("Starting Flask app - simulator will initialize on first request")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

