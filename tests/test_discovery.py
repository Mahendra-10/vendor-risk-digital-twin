"""
Unit tests for GCP Discovery module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.gcp_discovery import GCPDiscovery


class TestGCPDiscovery:
    """Test GCP Discovery functionality"""
    
    @pytest.fixture
    def discovery(self):
        """Create GCPDiscovery instance for testing"""
        with patch('scripts.gcp_discovery.functions_v1.CloudFunctionsServiceClient'):
            with patch('scripts.gcp_discovery.run_v2.ServicesClient'):
                return GCPDiscovery(project_id='test-project')
    
    def test_initialization(self, discovery):
        """Test GCPDiscovery initialization"""
        assert discovery.project_id == 'test-project'
        assert discovery.vendor_patterns is not None
        assert 'Stripe' in discovery.vendor_patterns
    
    def test_vendor_pattern_detection(self, discovery):
        """Test vendor pattern detection"""
        # Test environment variables
        env_vars = {
            'STRIPE_API_KEY': 'sk_test_xxx',
            'AUTH0_DOMAIN': 'example.auth0.com',
            'SENDGRID_API_KEY': 'SG.xxx',
            'RANDOM_VAR': 'value'
        }
        
        vendor_deps = {}
        discovery._extract_vendor_deps(
            vendor_deps,
            env_vars,
            'test-function',
            'cloud_function'
        )
        
        # Should detect Stripe, Auth0, and SendGrid
        assert 'Stripe' in vendor_deps
        assert 'Auth0' in vendor_deps
        assert 'SendGrid' in vendor_deps
        assert len(vendor_deps['Stripe']) == 1
    
    def test_analyze_vendors(self, discovery):
        """Test vendor analysis"""
        functions = [
            {
                'name': 'payment-api',
                'environment_variables': {
                    'STRIPE_API_KEY': 'sk_test_xxx',
                    'STRIPE_WEBHOOK_SECRET': 'whsec_xxx'
                }
            }
        ]
        
        services = [
            {
                'name': 'auth-service',
                'environment_variables': {
                    'AUTH0_DOMAIN': 'test.auth0.com'
                }
            }
        ]
        
        vendors = discovery._analyze_vendors(functions, services)
        
        assert len(vendors) == 2
        vendor_names = [v['name'] for v in vendors]
        assert 'Stripe' in vendor_names
        assert 'Auth0' in vendor_names
    
    def test_discover_all_structure(self, discovery):
        """Test discover_all returns correct structure"""
        with patch.object(discovery, '_discover_cloud_functions', return_value=[]):
            with patch.object(discovery, '_discover_cloud_run', return_value=[]):
                result = discovery.discover_all()
        
        # Check structure
        assert 'project_id' in result
        assert 'vendors' in result
        assert 'cloud_functions' in result
        assert 'cloud_run_services' in result
        assert result['project_id'] == 'test-project'
    
    def test_empty_environment_variables(self, discovery):
        """Test handling of empty environment variables"""
        vendor_deps = {}
        discovery._extract_vendor_deps(
            vendor_deps,
            {},
            'test-resource',
            'cloud_function'
        )
        
        # Should not crash and return empty
        assert len(vendor_deps) == 0
    
    def test_case_insensitive_detection(self, discovery):
        """Test case-insensitive vendor detection"""
        env_vars = {
            'stripe_api_key': 'sk_test_xxx',  # lowercase
            'STRIPE_SECRET': 'sk_test_yyy',   # uppercase
        }
        
        vendor_deps = {}
        discovery._extract_vendor_deps(
            vendor_deps,
            env_vars,
            'test-function',
            'cloud_function'
        )
        
        # Should detect both
        assert 'Stripe' in vendor_deps
        assert len(vendor_deps['Stripe']) == 2


class TestGCPDiscoveryIntegration:
    """Integration tests (require GCP credentials)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires GCP credentials")
    def test_real_gcp_discovery(self):
        """Test actual GCP API calls (skip by default)"""
        discovery = GCPDiscovery(project_id='your-real-project-id')
        result = discovery.discover_all()
        
        assert result is not None
        assert 'vendors' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

