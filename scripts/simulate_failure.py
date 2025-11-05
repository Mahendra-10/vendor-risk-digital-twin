"""
Vendor Failure Simulation Engine

Simulates vendor failure scenarios and predicts impact on:
- Operations (affected services, business processes)
- Finance (revenue loss, transaction failures)
- Compliance (control failures, framework score changes)

Usage:
    python scripts/simulate_failure.py --vendor "Stripe" --duration 4
"""

import argparse
import logging
from typing import Dict, List, Any
from datetime import datetime
from neo4j import GraphDatabase
from scripts.utils import (
    setup_logging,
    load_config,
    load_json_file,
    save_json_file,
    validate_env_vars,
    format_currency,
    format_percentage,
    calculate_impact_score
)


class VendorFailureSimulator:
    """Simulates vendor failure scenarios"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """
        Initialize simulator
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        self.logger = logging.getLogger(__name__)
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.config = load_config()
        self.compliance_data = load_json_file('data/sample/compliance_controls.json')
        self.logger.info("Simulator initialized")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    def simulate_vendor_failure(
        self, 
        vendor_name: str, 
        duration_hours: int
    ) -> Dict[str, Any]:
        """
        Simulate vendor failure and calculate impact
        
        Args:
            vendor_name: Name of the vendor
            duration_hours: Failure duration in hours
        
        Returns:
            Simulation results
        """
        self.logger.info(f"🔴 Simulating {vendor_name} failure for {duration_hours} hours...")
        
        simulation = {
            'vendor': vendor_name,
            'duration_hours': duration_hours,
            'timestamp': datetime.utcnow().isoformat(),
            'operational_impact': {},
            'financial_impact': {},
            'compliance_impact': {},
            'overall_impact_score': 0.0,
            'recommendations': []
        }
        
        # Calculate operational impact
        operational = self._calculate_operational_impact(vendor_name)
        simulation['operational_impact'] = operational
        
        # Calculate financial impact
        financial = self._calculate_financial_impact(vendor_name, duration_hours, operational)
        simulation['financial_impact'] = financial
        
        # Calculate compliance impact
        compliance = self._calculate_compliance_impact(vendor_name)
        simulation['compliance_impact'] = compliance
        
        # Calculate overall impact score
        simulation['overall_impact_score'] = calculate_impact_score(
            operational['impact_score'],
            financial['impact_score'],
            compliance['impact_score']
        )
        
        # Generate recommendations
        simulation['recommendations'] = self._generate_recommendations(simulation)
        
        self.logger.info(f"✅ Simulation complete. Impact score: {simulation['overall_impact_score']:.2f}")
        return simulation
    
    def _calculate_operational_impact(self, vendor_name: str) -> Dict[str, Any]:
        """
        Calculate operational impact
        
        Args:
            vendor_name: Vendor name
        
        Returns:
            Operational impact details
        """
        self.logger.info("Calculating operational impact...")
        
        with self.driver.session() as session:
            # Find affected services
            query = """
            MATCH (v:Vendor {name: $vendor_name})<-[:DEPENDS_ON]-(s:Service)
            OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
            RETURN s.name as service_name,
                   s.type as service_type,
                   s.rpm as rpm,
                   s.customers_affected as customers_affected,
                   collect(DISTINCT bp.name) as business_processes
            """
            result = session.run(query, vendor_name=vendor_name)
            
            affected_services = []
            total_rpm = 0
            customers_affected = 0
            business_processes = set()
            
            for record in result:
                service = {
                    'name': record['service_name'],
                    'type': record['service_type'],
                    'rpm': record['rpm'] or 0,
                    'customers_affected': record['customers_affected'] or 0,
                    'business_processes': record['business_processes']
                }
                affected_services.append(service)
                total_rpm += service['rpm']
                customers_affected = max(customers_affected, service['customers_affected'])
                business_processes.update(service['business_processes'])
        
        # Calculate impact score (0.0 to 1.0)
        impact_score = min(len(affected_services) / 10, 1.0)  # Normalize
        
        return {
            'affected_services': affected_services,
            'service_count': len(affected_services),
            'total_rpm': total_rpm,
            'customers_affected': customers_affected,
            'business_processes': sorted(list(business_processes)),
            'impact_score': impact_score
        }
    
    def _calculate_financial_impact(
        self, 
        vendor_name: str, 
        duration_hours: int,
        operational: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate financial impact
        
        Args:
            vendor_name: Vendor name
            duration_hours: Failure duration
            operational: Operational impact data
        
        Returns:
            Financial impact details
        """
        self.logger.info("Calculating financial impact...")
        
        # Get business metrics from config
        business_metrics = self.config['simulation']['business']
        revenue_per_hour = business_metrics['revenue_per_hour']
        
        # Calculate revenue loss based on affected services
        # Assume revenue loss proportional to number of critical services affected
        service_count = operational['service_count']
        revenue_loss_percentage = min(service_count * 0.25, 1.0)  # 25% per service, max 100%
        
        revenue_loss = revenue_per_hour * duration_hours * revenue_loss_percentage
        
        # Calculate transaction failures
        transactions_per_hour = business_metrics['transactions_per_hour']
        failed_transactions = int(transactions_per_hour * duration_hours * revenue_loss_percentage)
        
        # Customer impact cost (estimated)
        customers_affected = operational['customers_affected']
        customer_impact_cost = customers_affected * 5  # $5 per affected customer
        
        total_cost = revenue_loss + customer_impact_cost
        
        # Impact score
        impact_score = min(total_cost / 1000000, 1.0)  # Normalize to $1M
        
        return {
            'revenue_loss': revenue_loss,
            'revenue_loss_formatted': format_currency(revenue_loss),
            'failed_transactions': failed_transactions,
            'customer_impact_cost': customer_impact_cost,
            'total_cost': total_cost,
            'total_cost_formatted': format_currency(total_cost),
            'impact_score': impact_score
        }
    
    def _calculate_compliance_impact(self, vendor_name: str) -> Dict[str, Any]:
        """
        Calculate compliance impact
        
        Args:
            vendor_name: Vendor name
        
        Returns:
            Compliance impact details
        """
        self.logger.info("Calculating compliance impact...")
        
        # Get vendor's compliance controls
        control_mappings = self.compliance_data.get('control_mappings', {})
        vendor_controls = control_mappings.get(vendor_name, {})
        
        if not vendor_controls:
            return {
                'affected_frameworks': [],
                'impact_score': 0.0
            }
        
        # Get impact weights
        impact_weights = self.compliance_data.get('impact_weights', {})
        baseline = self.compliance_data.get('compliance_baseline', {})
        
        # Calculate impact for each framework
        frameworks = {}
        total_impact = 0
        
        for framework, control_ids in vendor_controls.items():
            framework_key = framework.replace('_controls', '')
            if framework_key not in impact_weights:
                continue
            
            # Calculate score reduction
            score_reduction = sum(
                impact_weights[framework_key].get(ctrl, 0.05)
                for ctrl in control_ids
            )
            
            baseline_score = baseline.get(f"{framework_key}_score", 0.90)
            new_score = max(baseline_score - score_reduction, 0.0)
            
            frameworks[framework_key] = {
                'baseline_score': baseline_score,
                'new_score': new_score,
                'score_change': score_reduction,
                'affected_controls': control_ids
            }
            
            total_impact += score_reduction
        
        # Overall compliance impact score
        impact_score = min(total_impact / len(frameworks) if frameworks else 0, 1.0)
        
        return {
            'affected_frameworks': frameworks,
            'impact_score': impact_score,
            'summary': {
                framework: {
                    'change': format_percentage(data['score_change']),
                    'new_score': format_percentage(data['new_score'])
                }
                for framework, data in frameworks.items()
            }
        }
    
    def _generate_recommendations(self, simulation: Dict[str, Any]) -> List[str]:
        """
        Generate remediation recommendations
        
        Args:
            simulation: Simulation results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        vendor = simulation['vendor']
        
        # Operational recommendations
        service_count = simulation['operational_impact']['service_count']
        if service_count > 0:
            recommendations.append(
                f"Implement fallback mechanisms for {service_count} services depending on {vendor}"
            )
            recommendations.append(
                f"Consider vendor diversification for critical business processes"
            )
        
        # Financial recommendations
        total_cost = simulation['financial_impact']['total_cost']
        if total_cost > 100000:
            recommendations.append(
                f"High financial impact detected ({format_currency(total_cost)}). "
                f"Implement circuit breakers and graceful degradation"
            )
        
        # Compliance recommendations
        compliance = simulation['compliance_impact']
        if compliance['impact_score'] > 0.1:
            recommendations.append(
                f"Compliance impact significant. Review compensating controls for affected frameworks"
            )
            for framework, data in compliance['summary'].items():
                recommendations.append(
                    f"  - {framework.upper()}: Score drops to {data['new_score']}"
                )
        
        return recommendations


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Simulate vendor failure scenarios'
    )
    parser.add_argument(
        '--vendor',
        required=True,
        help='Vendor name (e.g., "Stripe", "Auth0")'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=4,
        help='Failure duration in hours'
    )
    parser.add_argument(
        '--output',
        default='data/outputs/simulation_result.json',
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
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
    if not validate_env_vars(required_vars):
        logger.error("Please configure Neo4j credentials in .env file")
        return 1
    
    # Load config
    config = load_config()
    neo4j_config = config['neo4j']
    
    # Run simulation
    simulator = None
    try:
        simulator = VendorFailureSimulator(
            neo4j_uri=neo4j_config['uri'],
            neo4j_user=neo4j_config['user'],
            neo4j_password=neo4j_config['password']
        )
        
        result = simulator.simulate_vendor_failure(args.vendor, args.duration)
        
        # Save results
        save_json_file(result, args.output)
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info(f"VENDOR FAILURE SIMULATION: {args.vendor}")
        logger.info("="*60)
        logger.info(f"\n📊 OPERATIONAL IMPACT:")
        logger.info(f"   - Services Affected: {result['operational_impact']['service_count']}")
        logger.info(f"   - Customers Affected: {result['operational_impact']['customers_affected']:,}")
        logger.info(f"   - Business Processes: {len(result['operational_impact']['business_processes'])}")
        
        logger.info(f"\n💰 FINANCIAL IMPACT:")
        logger.info(f"   - Total Cost: {result['financial_impact']['total_cost_formatted']}")
        logger.info(f"   - Revenue Loss: {result['financial_impact']['revenue_loss_formatted']}")
        logger.info(f"   - Failed Transactions: {result['financial_impact']['failed_transactions']:,}")
        
        logger.info(f"\n🔒 COMPLIANCE IMPACT:")
        for framework, data in result['compliance_impact']['summary'].items():
            logger.info(f"   - {framework.upper()}: {data['change']} → {data['new_score']}")
        
        logger.info(f"\n⚠️  OVERALL IMPACT SCORE: {result['overall_impact_score']:.2f}/1.0")
        
        logger.info(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result['recommendations'], 1):
            logger.info(f"   {i}. {rec}")
        
        logger.info(f"\n✅ Results saved to: {args.output}")
        logger.info("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        return 1
    
    finally:
        if simulator:
            simulator.close()


if __name__ == "__main__":
    exit(main())

