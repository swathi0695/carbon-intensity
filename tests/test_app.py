import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Mock Data for testing
mock_data = [
    {"datetime": "2024-10-24T10:00:00.000Z", "carbonIntensity": 200},
    {"datetime": "2024-10-24T11:00:00.000Z", "carbonIntensity": 210},
    {"datetime": "2024-10-24T12:00:00.000Z", "carbonIntensity": 190}
]

mock_average_intensity = sum([200, 210, 190]) / len([200, 210, 190])


def test_index_page(client, monkeypatch):
    """Test if the index page displays correctly with average carbon intensity."""
    
    def mock_get_carbon_intensity_data():
        return mock_data
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/')
    assert response.status_code == 200
    assert b'The average carbon intensity in the last 24 hours' in response.data
    assert str(mock_average_intensity).encode() in response.data  # Check that the average is displayed


def test_api_view_data(client, monkeypatch):
    """Test if the /view_data endpoint returns the correct mock data."""
    
    def mock_get_carbon_intensity_data():
        return mock_data
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/view_data')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == len(mock_data)
    assert data[0]['carbonIntensity'] == mock_data[0]['carbonIntensity']


def test_download_csv(client, monkeypatch):
    """Test the /download_csv endpoint for valid CSV output."""
    
    def mock_get_carbon_intensity_data():
        return mock_data
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/download_csv')
    
    assert response.status_code == 200
    assert "attachment; filename=carbon_intensity.csv" in response.headers['Content-Disposition']
    assert "text/csv" in response.headers['Content-Type']
    
    csv_content = response.data.decode('utf-8')
    
    # Check that CSV has correct headers and data
    assert "Hour,Carbon Intensity (gCO2eq/kWh)" in csv_content
    assert "2024-10-24 10:00:00,200" in csv_content
    assert "2024-10-24 11:00:00,210" in csv_content
    assert "Average," in csv_content
    assert str(mock_average_intensity) in csv_content  # Check if average is included


def test_api_no_data(client, monkeypatch):
    """Test if the /view_data endpoint handles the case when no data is returned."""
    
    def mock_get_carbon_intensity_data():
        return []
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/view_data')
    data = response.get_json()
    
    assert response.status_code == 200
    assert data == []  # No data should return an empty list


def test_api_error_handling(client, monkeypatch):
    """Test if the API returns a 500 error when the external service fails."""
    
    def mock_get_carbon_intensity_data():
        return None  # Simulate failure to get data
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/view_data')
    assert response.status_code == 500  # Expect a server error
    data = response.get_json()
    assert "error" in data
    assert data['error'] == "Failed to retrieve data"


def test_csv_no_data(client, monkeypatch):
    """Test /download_csv to ensure proper handling of no data scenario."""
    
    def mock_get_carbon_intensity_data():
        return None
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/download_csv')
    assert response.status_code == 500  # Should return 500 when no data is available
    assert b"Failed to retrieve data" in response.data


def test_index_page_no_data(client, monkeypatch):
    """Test index page when no data is returned."""
    
    def mock_get_carbon_intensity_data():
        return None
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/')
    print("resssp..", response)
    assert response.status_code == 500  # Should fail when there's no data
    assert b"Failed to retrieve data" in response.data


def test_csv_with_average_zero(client, monkeypatch):
    """Test CSV generation when all carbon intensities are zero (edge case)."""
    
    def mock_get_carbon_intensity_data():
        return [
            {"datetime": "2024-10-24T10:00:00.000Z", "carbonIntensity": 0},
            {"datetime": "2024-10-24T11:00:00.000Z", "carbonIntensity": 0}
        ]
    
    monkeypatch.setattr('app.get_carbon_intensity_data', mock_get_carbon_intensity_data)
    
    response = client.get('/download_csv')
    assert response.status_code == 200
    csv_content = response.data.decode('utf-8')
    
    assert "Hour,Carbon Intensity (gCO2eq/kWh)" in csv_content
    assert "2024-10-24 10:00:00,0" in csv_content
    assert "2024-10-24 11:00:00,0" in csv_content
    assert "Average,0.0" in csv_content  # Ensure average is 0.0
