"""
External API client with automatic fallback to open public data.
Handles weather, outbreak, and epidemiology data retrieval with graceful degradation.
"""

import logging
import requests
import json
import csv
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class WeatherClient:
    """Weather data retrieval with fallback to Open-Meteo"""

    @staticmethod
    def get_weather(latitude: float, longitude: float, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather data for location.
        Tries OpenWeather first, falls back to Open-Meteo if key missing.
        """
        if api_key:
            return WeatherClient._get_openweather(latitude, longitude, api_key)
        else:
            logger.info("No OpenWeather key, using Open-Meteo fallback")
            return WeatherClient._get_open_meteo(latitude, longitude)

    @staticmethod
    def _get_openweather(latitude: float, longitude: float, api_key: str) -> Dict[str, Any]:
        """Get data from OpenWeather API"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenWeather API failed: {e}, falling back to Open-Meteo")
            return WeatherClient._get_open_meteo(latitude, longitude)

    @staticmethod
    def _get_open_meteo(latitude: float, longitude: float) -> Dict[str, Any]:
        """Get data from Open-Meteo (free, no key required)"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,precipitation",
                "timezone": "auto"
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return {
                "current": {
                    "temp": data["current"]["temperature_2m"],
                    "humidity": data["current"]["relative_humidity_2m"],
                    "precipitation": data["current"]["precipitation"]
                }
            }
        except Exception as e:
            logger.error(f"Open-Meteo API failed: {e}")
            return {"error": str(e), "source": "open-meteo"}


class OutbreakClient:
    """Outbreak data retrieval with fallback to mock data"""

    MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/mock/sormas_outbreaks.json")

    @staticmethod
    def get_outbreaks(api_key: Optional[str] = None, api_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active outbreak data.
        Tries SORMAS API first, falls back to mock data if key missing.
        """
        if api_key and api_url:
            result = OutbreakClient._get_sormas_outbreaks(api_key, api_url)
            if result is not None:
                return result
        
        logger.info("Using mock outbreak data (fallback)")
        return OutbreakClient._get_mock_outbreaks()

    @staticmethod
    def _get_sormas_outbreaks(api_key: str, api_url: str) -> Optional[List[Dict[str, Any]]]:
        """Get data from SORMAS API"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(f"{api_url}/outbreaks", headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"SORMAS API failed: {e}")
            return None

    @staticmethod
    def _get_mock_outbreaks() -> List[Dict[str, Any]]:
        """Load mock outbreak data from JSON file"""
        try:
            if os.path.exists(OutbreakClient.MOCK_DATA_FILE):
                with open(OutbreakClient.MOCK_DATA_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mock outbreak data: {e}")
        
        # Fallback mock data
        return [
            {
                "id": "mock-1",
                "disease": "Lassa Fever",
                "region": "Edo State",
                "cases": 5,
                "deaths": 1,
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "mock-2",
                "disease": "Lassa Fever",
                "region": "Bauchi State",
                "cases": 3,
                "deaths": 0,
                "last_updated": datetime.now().isoformat()
            }
        ]


class EpidemiologyClient:
    """Disease epidemiology data with fallback to CSV"""

    MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/mock/cdc_trends.csv")

    @staticmethod
    def get_disease_trends(disease: str = "lassa_fever", api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get disease trend data.
        Tries CDC API first, falls back to CSV if key missing.
        """
        if api_key:
            result = EpidemiologyClient._get_cdc_trends(disease, api_key)
            if result is not None:
                return result
        
        logger.info("Using CDC epidemiology CSV (fallback)")
        return EpidemiologyClient._get_mock_trends(disease)

    @staticmethod
    def _get_cdc_trends(disease: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Get data from CDC API"""
        try:
            headers = {"X-API-Key": api_key}
            response = requests.get(
                f"https://api.cdc.gov/disease/{disease}/trends",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"CDC API failed: {e}")
            return None

    @staticmethod
    def _get_mock_trends(disease: str) -> Dict[str, Any]:
        """Load mock epidemiology data from CSV"""
        trends = []
        try:
            if os.path.exists(EpidemiologyClient.MOCK_DATA_FILE):
                with open(EpidemiologyClient.MOCK_DATA_FILE, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if disease.lower() in row.get("disease", "").lower():
                            trends.append(row)
        except Exception as e:
            logger.error(f"Failed to load mock trends: {e}")
        
        # Fallback trends
        if not trends:
            trends = [
                {
                    "week": datetime.now().isocalendar()[1],
                    "year": datetime.now().year,
                    "disease": "Lassa Fever",
                    "cases": 42,
                    "deaths": 8,
                    "case_fatality_rate": 0.19
                }
            ]
        
        return {"trends": trends, "source": "mock" if not os.path.exists(EpidemiologyClient.MOCK_DATA_FILE) else "csv"}


class NigeriaHealthClient:
    """Nigeria-specific health data with fallback to CSV"""

    MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/mock/nigeria_health.csv")

    @staticmethod
    def get_state_health_data(state: str, api_key: Optional[str] = None, api_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Nigeria state health data.
        Tries NPHCDA API first, falls back to CSV if key missing.
        """
        if api_key and api_url:
            result = NigeriaHealthClient._get_nphcda_data(state, api_key, api_url)
            if result is not None:
                return result
        
        logger.info("Using Nigeria health CSV (fallback)")
        return NigeriaHealthClient._get_mock_state_data(state)

    @staticmethod
    def _get_nphcda_data(state: str, api_key: str, api_url: str) -> Optional[Dict[str, Any]]:
        """Get data from NPHCDA API"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                f"{api_url}/states/{state}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"NPHCDA API failed: {e}")
            return None

    @staticmethod
    def _get_mock_state_data(state: str) -> Dict[str, Any]:
        """Load mock Nigeria state health data"""
        try:
            if os.path.exists(NigeriaHealthClient.MOCK_DATA_FILE):
                with open(NigeriaHealthClient.MOCK_DATA_FILE, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("state", "").lower() == state.lower():
                            return row
        except Exception as e:
            logger.error(f"Failed to load mock Nigeria data: {e}")
        
        # Fallback data
        return {
            "state": state,
            "population": 3000000,
            "health_facilities": 45,
            "rodent_control_units": 3,
            "outbreak_alerts": 2
        }
