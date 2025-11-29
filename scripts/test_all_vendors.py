"""
Test All Vendors Simulation

Tests that all vendors in Neo4j can be properly simulated without issues.
This ensures vendor name normalization works correctly for all vendors.

Usage:
    python scripts/test_all_vendors.py
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from scripts.utils import setup_logging, load_config, validate_env_vars
from scripts.simulate_failure import VendorFailureSimulator

logger = logging.getLogger(__name__)


def test_all_vendors():
    """Test simulation for all vendors"""
    setup_logging('INFO')
    
    # Validate environment
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Please configure Neo4j credentials in .env file")
        return 1
    
    config = load_config()
    neo4j_config = config['neo4j']
    
    # Initialize simulator
    simulator = VendorFailureSimulator(
        neo4j_uri=neo4j_config['uri'],
        neo4j_user=neo4j_config['user'],
        neo4j_password=neo4j_config['password']
    )
    
    try:
        # Get all vendors from Neo4j
        with simulator.driver.session() as session:
            result = session.run('''
                MATCH (v:Vendor)
                RETURN DISTINCT COALESCE(v.display_name, v.name) as display_name,
                       v.name as normalized_name
                ORDER BY display_name
            ''')
            
            vendors = []
            for record in result:
                vendors.append({
                    'display_name': record['display_name'],
                    'normalized_name': record['normalized_name']
                })
        
        logger.info(f"Found {len(vendors)} vendors to test")
        logger.info("=" * 80)
        
        # Test each vendor
        all_passed = True
        for vendor in vendors:
            display_name = vendor['display_name']
            normalized_name = vendor['normalized_name']
            
            logger.info(f"\n🧪 Testing: {display_name} (normalized: {normalized_name})")
            
            try:
                # Run simulation (this will use normalized name internally)
                result = simulator.simulate_vendor_failure(display_name, 4)
                
                # Check results
                service_count = result.get('operational_impact', {}).get('service_count', 0)
                has_compliance = bool(result.get('compliance_impact', {}).get('affected_frameworks', {}))
                
                if service_count > 0:
                    logger.info(f"  ✅ PASS: Found {service_count} services")
                    if has_compliance:
                        logger.info(f"  ✅ PASS: Compliance impact calculated")
                    else:
                        logger.info(f"  ℹ️  INFO: No compliance data (expected for some vendors)")
                else:
                    logger.warning(f"  ⚠️  WARNING: No services found for {display_name}")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"  ❌ FAIL: Error simulating {display_name}: {e}")
                all_passed = False
        
        logger.info("\n" + "=" * 80)
        if all_passed:
            logger.info("✅ All vendors tested successfully!")
        else:
            logger.warning("⚠️  Some vendors had issues")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    finally:
        simulator.close()


if __name__ == "__main__":
    exit(test_all_vendors())

