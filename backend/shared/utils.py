import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from functools import wraps
import numpy as np
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

def async_to_sync(async_func):
    """Decorator to run async functions in sync context."""
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates."""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula."""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def normalize_environmental_data(data: Dict) -> Dict:
    """Normalize environmental data for ML processing."""
    normalized = {}
    
    # Temperature normalization (Celsius to 0-1 scale, assuming -50 to 50°C range)
    if 'temperature' in data:
        temp = float(data['temperature'])
        normalized['temperature'] = (temp + 50) / 100
    
    # Rainfall normalization (mm to 0-1 scale, assuming 0-500mm range)
    if 'rainfall' in data:
        rainfall = float(data['rainfall'])
        normalized['rainfall'] = min(rainfall / 500, 1.0)
    
    # Humidity normalization (percentage to 0-1 scale)
    if 'humidity' in data:
        humidity = float(data['humidity'])
        normalized['humidity'] = humidity / 100
    
    # Vegetation index (already 0-1 scale typically)
    if 'vegetation_index' in data:
        normalized['vegetation_index'] = float(data['vegetation_index'])
    
    # Elevation normalization (meters, assuming 0-3000m range)
    if 'elevation' in data:
        elevation = float(data['elevation'])
        normalized['elevation'] = min(elevation / 3000, 1.0)
    
    return normalized

def calculate_habitat_suitability_score(environmental_data: Dict) -> float:
    """Calculate habitat suitability score based on environmental factors."""
    normalized_data = normalize_environmental_data(environmental_data)
    
    # Mastomys Natalensis habitat preferences (based on research)
    optimal_conditions = {
        'temperature': 0.6,  # ~20-25°C
        'rainfall': 0.4,     # Moderate rainfall
        'humidity': 0.7,     # High humidity
        'vegetation_index': 0.5,  # Moderate vegetation
        'elevation': 0.3     # Lower elevations
    }
    
    # Calculate weighted score
    weights = {
        'temperature': 0.25,
        'rainfall': 0.20,
        'humidity': 0.20,
        'vegetation_index': 0.20,
        'elevation': 0.15
    }
    
    score = 0.0
    total_weight = 0.0
    
    for factor, optimal_value in optimal_conditions.items():
        if factor in normalized_data:
            # Calculate how close the actual value is to optimal
            difference = abs(normalized_data[factor] - optimal_value)
            factor_score = 1.0 - difference
            score += factor_score * weights[factor]
            total_weight += weights[factor]
    
    # Normalize by total weight used
    if total_weight > 0:
        score = score / total_weight
    
    return max(0.0, min(1.0, score))

def detect_environmental_anomalies(data_points: List[Dict]) -> List[Dict]:
    """Detect anomalies in environmental data using statistical methods."""
    if len(data_points) < 10:
        return []  # Need sufficient data for anomaly detection
    
    df = pd.DataFrame(data_points)
    anomalies = []
    
    # Check each numeric column for outliers using IQR method
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    for column in numeric_columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Find outliers
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        
        for idx, row in outliers.iterrows():
            anomalies.append({
                'index': int(idx),
                'column': column,
                'value': float(row[column]),
                'expected_range': [float(lower_bound), float(upper_bound)],
                'severity': 'high' if (row[column] < lower_bound - IQR or row[column] > upper_bound + IQR) else 'medium',
                'timestamp': row.get('timestamp', datetime.now(timezone.utc).isoformat())
            })
    
    return anomalies

def format_api_response(data: Any, status: str = 'success', message: str = None) -> Dict:
    """Format standardized API response."""
    response = {
        'status': status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data': data
    }
    
    if message:
        response['message'] = message
    
    return response

def validate_detection_data(data: Dict) -> List[str]:
    """Validate detection pattern data."""
    errors = []
    
    required_fields = ['latitude', 'longitude', 'detection_timestamp']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'latitude' in data and 'longitude' in data:
        if not validate_coordinates(data['latitude'], data['longitude']):
            errors.append("Invalid coordinates")
    
    if 'confidence_score' in data:
        score = data['confidence_score']
        if not (0 <= score <= 1):
            errors.append("Confidence score must be between 0 and 1")
    
    return errors

def calculate_risk_level(suitability_score: float, detection_count: int, recent_activity: bool) -> str:
    """Calculate overall risk level for outbreak prediction."""
    risk_score = 0
    
    # Habitat suitability contribution (40%)
    risk_score += suitability_score * 0.4
    
    # Detection frequency contribution (40%)
    detection_factor = min(detection_count / 10, 1.0)  # Normalize to 0-1
    risk_score += detection_factor * 0.4
    
    # Recent activity contribution (20%)
    if recent_activity:
        risk_score += 0.2
    
    # Classify risk level
    if risk_score >= 0.8:
        return 'critical'
    elif risk_score >= 0.6:
        return 'high'
    elif risk_score >= 0.4:
        return 'medium'
    elif risk_score >= 0.2:
        return 'low'
    else:
        return 'minimal'

def generate_alert_message(risk_level: str, location: Dict, details: Dict) -> str:
    """Generate human-readable alert message."""
    location_str = f"({details.get('region', 'Unknown region')})"
    
    messages = {
        'critical': f"🚨 CRITICAL ALERT: High Mastomys activity detected at {location_str}. Immediate intervention recommended.",
        'high': f"⚠️ HIGH RISK: Elevated Mastomys population detected at {location_str}. Enhanced monitoring advised.",
        'medium': f"📊 MEDIUM RISK: Moderate Mastomys activity at {location_str}. Continue routine monitoring.",
        'low': f"📈 LOW RISK: Minor Mastomys activity detected at {location_str}. Standard protocols sufficient.",
        'minimal': f"✅ MINIMAL RISK: Low Mastomys activity at {location_str}. No immediate action required."
    }
    
    return messages.get(risk_level, f"Risk level {risk_level} detected at {location_str}")

class DataProcessor:
    """Utility class for data processing operations."""
    
    @staticmethod
    def clean_sensor_data(raw_data: List[Dict]) -> List[Dict]:
        """Clean and validate sensor data."""
        cleaned_data = []
        
        for record in raw_data:
            # Remove null values and invalid entries
            if not record or not isinstance(record, dict):
                continue
            
            # Validate timestamp
            if 'timestamp' not in record:
                record['timestamp'] = datetime.now(timezone.utc).isoformat()
            
            # Validate numeric fields
            numeric_fields = ['temperature', 'humidity', 'rainfall']
            for field in numeric_fields:
                if field in record:
                    try:
                        record[field] = float(record[field])
                    except (ValueError, TypeError):
                        record[field] = None
            
            cleaned_data.append(record)
        
        return cleaned_data
    
    @staticmethod
    def aggregate_detection_data(detections: List[Dict], time_window: str = '1h') -> Dict:
        """Aggregate detection data by time window."""
        if not detections:
            return {'total_detections': 0, 'avg_confidence': 0, 'locations': []}
        
        df = pd.DataFrame(detections)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['detection_timestamp'])
        
        # Group by time window
        if time_window == '1h':
            grouped = df.groupby(pd.Grouper(key='timestamp', freq='H'))
        elif time_window == '1d':
            grouped = df.groupby(pd.Grouper(key='timestamp', freq='D'))
        else:
            grouped = df.groupby(pd.Grouper(key='timestamp', freq='H'))
        
        aggregated = {
            'total_detections': len(detections),
            'avg_confidence': float(df['confidence_score'].mean()) if 'confidence_score' in df else 0,
            'unique_locations': len(df[['latitude', 'longitude']].drop_duplicates()),
            'time_series': []
        }
        
        for name, group in grouped:
            if not group.empty:
                aggregated['time_series'].append({
                    'timestamp': name.isoformat(),
                    'count': len(group),
                    'avg_confidence': float(group['confidence_score'].mean()) if 'confidence_score' in group else 0
                })
        
        return aggregated
