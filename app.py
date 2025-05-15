"""
Pytest tests for the Flask application.
"""
import sys
import os
import pytest

# Add the project root to the Python path to allow importing the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app instance from the updated app file
# Assuming app_v2_performance.py is in the root directory /home/ubuntu/
from app_v2_performance import app as flask_app

@pytest.fixture
def client():
    """Provides a test client for the Flask application."""
    flask_app.config['TESTING'] = True
    # Disable actual client initialization during tests if they make external calls
    # For now, we rely on the app's behavior when clients are None (e.g., due to missing creds in test env)
    # A more robust solution would involve mocking the API clients.
    with flask_app.test_client() as client:
        yield client

def test_api_status(client):
    """Test the /api/status endpoint."""
    response = client.get('/api/status')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'meta' in json_data
    assert 'google_analytics' in json_data
    assert 'google_ads' in json_data
    assert isinstance(json_data['meta']['connected'], bool)
    assert isinstance(json_data['google_analytics']['connected'], bool)
    assert isinstance(json_data['google_ads']['connected'], bool)

# --- Meta API Tests ---
def test_meta_campaigns_validation(client):
    """Test /api/meta/campaigns input validation."""
    # Valid request (default date_preset)
    response_valid = client.get('/api/meta/campaigns')
    # Expect 500 if client is None, but not 400 for validation
    assert response_valid.status_code != 400 

    # Valid request with parameter
    response_valid_param = client.get('/api/meta/campaigns?date_preset=last_7d')
    assert response_valid_param.status_code != 400

def test_meta_insights_validation(client):
    """Test /api/meta/insights input validation."""
    response_valid = client.get('/api/meta/insights?date_preset=last_14d&level=ad')
    assert response_valid.status_code != 400

# --- Google Analytics API Tests ---
def test_ga_traffic_sources_validation(client):
    """Test /api/ga/traffic_sources input validation for 'limit'."""
    # Valid limit
    response_valid = client.get('/api/ga/traffic_sources?limit=5')
    assert response_valid.status_code != 400

    # Invalid limit (too low)
    response_invalid_low = client.get('/api/ga/traffic_sources?limit=0')
    assert response_invalid_low.status_code == 400
    json_data_low = response_invalid_low.get_json()
    assert json_data_low['error'] == 'Validation Error'
    assert any(d['type'] == 'greater_than_equal' for d in json_data_low['details'])

    # Invalid limit (too high)
    response_invalid_high = client.get('/api/ga/traffic_sources?limit=101')
    assert response_invalid_high.status_code == 400
    json_data_high = response_invalid_high.get_json()
    assert json_data_high['error'] == 'Validation Error'
    assert any(d['type'] == 'less_than_equal' for d in json_data_high['details'])

    # Invalid limit (not an integer)
    response_invalid_type = client.get('/api/ga/traffic_sources?limit=abc')
    assert response_invalid_type.status_code == 400
    json_data_type = response_invalid_type.get_json()
    assert json_data_type['error'] == 'Validation Error'
    assert any(d['type'] == 'int_parsing' for d in json_data_type['details'])

# --- Google Ads API Tests ---
def test_ads_summary_validation(client):
    """Test /api/ads/summary input validation for 'days'."""
    # Valid days
    response_valid = client.get('/api/ads/summary?days=15')
    assert response_valid.status_code != 400

    # Invalid days (too low)
    response_invalid_low = client.get('/api/ads/summary?days=0')
    assert response_invalid_low.status_code == 400
    json_data_low = response_invalid_low.get_json()
    assert json_data_low['error'] == 'Validation Error'

    # Invalid days (too high)
    response_invalid_high = client.get('/api/ads/summary?days=400')
    assert response_invalid_high.status_code == 400
    json_data_high = response_invalid_high.get_json()
    assert json_data_high['error'] == 'Validation Error'

# --- Dashboard Overview Test ---
def test_dashboard_overview_validation(client):
    """Test /api/dashboard/overview input validation for 'days'."""
    response_valid = client.get('/api/dashboard/overview?days=60')
    assert response_valid.status_code != 400

    response_invalid = client.get('/api/dashboard/overview?days=0')
    assert response_invalid.status_code == 400

