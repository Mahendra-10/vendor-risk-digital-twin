"""
Unit tests for Vendor Failure Simulation module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.simulation.simulate_failure import VendorFailureSimulator


class TestVendorFailureSimulator:
    """Test Vendor Failure Simulator"""
    
    @pytest.fixture
    def simulator(self):
        """Create simulator instance for testing"""
        with patch('scripts.simulation.simulate_failure.GraphDatabase.driver'):
            sim = VendorFailureSimulator(
                neo4j_uri='bolt://localhost:7687',
                neo4j_user='neo4j',
                neo4j_password='password'
            )
            return sim
    
    def test_initialization(self, simulator):
        """Test simulator initialization"""
        assert simulator.config is not None
        assert simulator.compliance_data is not None
    
    def test_operational_impact_calculation(self, simulator):
        """Test operational impact calculation"""
        # Mock Neo4j session
        mock_session = MagicMock()
        mock_result = [
            {
                'service_name': 'payment-api',
                'service_type': 'cloud_function',
                'rpm': 500,
                'customers_affected': 50000,
                'business_processes': ['checkout', 'refunds']
            },
            {
                'service_name': 'checkout-service',
                'service_type': 'cloud_run',
                'rpm': 800,
                'customers_affected': 50000,
                'business_processes': ['checkout']
            }
        ]
        mock_session.run.return_value = mock_result
        
        with patch.object(simulator.driver, 'session', return_value=mock_session):
            impact = simulator._calculate_operational_impact('Stripe')
        
        assert 'affected_services' in impact
        assert 'service_count' in impact
        assert 'total_rpm' in impact
        assert 'customers_affected' in impact
        assert 'impact_score' in impact
        
        # Verify calculations
        assert impact['service_count'] == 2
        assert impact['total_rpm'] == 1300
        assert impact['customers_affected'] == 50000
    
    def test_financial_impact_calculation(self, simulator):
        """Test financial impact calculation"""
        operational = {
            'service_count': 2,
            'customers_affected': 50000
        }
        
        impact = simulator._calculate_financial_impact(
            vendor_name='Stripe',
            duration_hours=4,
            operational=operational
        )
        
        assert 'revenue_loss' in impact
        assert 'failed_transactions' in impact
        assert 'total_cost' in impact
        assert 'impact_score' in impact
        
        # Revenue loss should be calculated
        assert impact['revenue_loss'] > 0
        assert impact['total_cost'] > 0
    
    def test_compliance_impact_calculation(self, simulator):
        """Test compliance impact calculation"""
        impact = simulator._calculate_compliance_impact('Stripe')
        
        assert 'affected_frameworks' in impact
        assert 'impact_score' in impact
        
        # Should have framework data if vendor is mapped
        if impact['affected_frameworks']:
            for framework, data in impact['affected_frameworks'].items():
                assert 'baseline_score' in data
                assert 'new_score' in data
                assert 'score_change' in data
    
    def test_recommendation_generation(self, simulator):
        """Test recommendation generation"""
        simulation = {
            'vendor': 'Stripe',
            'operational_impact': {
                'service_count': 2,
                'customers_affected': 50000
            },
            'financial_impact': {
                'total_cost': 500000
            },
            'compliance_impact': {
                'impact_score': 0.15,
                'summary': {
                    'soc2': {'change': '-16%', 'new_score': '76%'}
                }
            }
        }
        
        recommendations = simulator._generate_recommendations(simulation)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_zero_impact_scenario(self, simulator):
        """Test scenario where vendor has no impact"""
        mock_session = MagicMock()
        mock_session.run.return_value = []
        
        with patch.object(simulator.driver, 'session', return_value=mock_session):
            impact = simulator._calculate_operational_impact('UnknownVendor')
        
        assert impact['service_count'] == 0
        assert impact['total_rpm'] == 0
        assert impact['impact_score'] == 0.0
    
    def test_simulation_result_structure(self, simulator):
        """Test that simulation returns correct structure"""
        # Mock all calculation methods
        with patch.object(simulator, '_calculate_operational_impact') as mock_op:
            with patch.object(simulator, '_calculate_financial_impact') as mock_fin:
                with patch.object(simulator, '_calculate_compliance_impact') as mock_comp:
                    with patch.object(simulator, '_generate_recommendations') as mock_rec:
                        # Setup mocks
                        mock_op.return_value = {'impact_score': 0.5}
                        mock_fin.return_value = {'impact_score': 0.6}
                        mock_comp.return_value = {'impact_score': 0.7}
                        mock_rec.return_value = ['Test recommendation']
                        
                        result = simulator.simulate_vendor_failure('Stripe', 4)
        
        # Check structure
        assert 'vendor' in result
        assert 'duration_hours' in result
        assert 'operational_impact' in result
        assert 'financial_impact' in result
        assert 'compliance_impact' in result
        assert 'overall_impact_score' in result
        assert 'recommendations' in result
        
        # Check values
        assert result['vendor'] == 'Stripe'
        assert result['duration_hours'] == 4
        assert 0.0 <= result['overall_impact_score'] <= 1.0


class TestImpactScoreCalculation:
    """Test impact score calculation logic"""
    
    def test_weighted_score_calculation(self):
        """Test weighted impact score calculation"""
        from scripts.utils import calculate_impact_score
        
        score = calculate_impact_score(
            operational_impact=0.8,
            financial_impact=0.6,
            compliance_impact=0.7
        )
        
        # Default weights: operational=0.4, financial=0.35, compliance=0.25
        # Expected: 0.8*0.4 + 0.6*0.35 + 0.7*0.25 = 0.32 + 0.21 + 0.175 = 0.705
        assert 0.7 <= score <= 0.71
    
    def test_custom_weights(self):
        """Test custom weight calculation"""
        from scripts.utils import calculate_impact_score
        
        weights = {
            'operational': 0.5,
            'financial': 0.3,
            'compliance': 0.2
        }
        
        score = calculate_impact_score(
            operational_impact=1.0,
            financial_impact=0.5,
            compliance_impact=0.0,
            weights=weights
        )
        
        # Expected: 1.0*0.5 + 0.5*0.3 + 0.0*0.2 = 0.65
        assert score == 0.65
    
    def test_score_bounds(self):
        """Test that score is always between 0 and 1"""
        from scripts.utils import calculate_impact_score
        
        # Test maximum
        score_max = calculate_impact_score(1.0, 1.0, 1.0)
        assert score_max == 1.0
        
        # Test minimum
        score_min = calculate_impact_score(0.0, 0.0, 0.0)
        assert score_min == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

