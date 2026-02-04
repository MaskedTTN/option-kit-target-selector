import pytest
from httpx import AsyncClient
from main import app
from dependencies.VIDDatabase import VIDDatabase
from dependencies.VIDFetcher import VIDFetcher
from models import VehicleSelectionRequest
import os

# 1. Setup Mock Database for Testing
@pytest.fixture(scope="session")
def test_db():
    db_path = "test_vid_cache.db"
    db = VIDDatabase(db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

# 2. Test the API Health Check
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

# 3. Test Database Cache Logic (Unit Test)
""" def test_database_caching(test_db):
    sample_data = {
        'vid': 'TEST-VID-123',
        'series': 'F22N',
        'body': 'Cou',
        'model': 'M240i',
        'market': 'EUR',
        'production': '20181100',
        'engine': 'B58',
        'steering': 'R',
        'url': 'https://realoem.com/test'
    }
    
    # Save to DB
    test_db.save_vid(sample_data)
    
    # Retrieve from DB
    cached = test_db.get_vid(
        series='F22N', 
        model='M240i', 
        production='20181100'
    )
    
    assert cached is not None
    assert cached['vid'] == 'TEST-VID-123' """

# 4. Integration Test: RealOEM Fetcher (Requires Browser/Xvfb)
# We mark this so we can skip it if we don't want to run the browser
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_oem_fetch():
    selection = VehicleSelectionRequest(
        series="F22N",
        body="Cou",
        model="M240i",
        market="EUR",
        production="20181100",
        engine="B58",
        steering="R"
    )
    
    # This will actually trigger nodriver inside the container
    result = await VIDFetcher.fetch_vid(selection)
    
    assert result is not None
    assert "vid" in result
    assert result["series"] == "F22N"