import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import joblib
import os
from .models.habitat_predictor import HabitatPredictor
from .models.movement_predictor import MovementPredictor
from .models.anomaly_detector import AnomalyDetector
from shared.database import get_neon_sql, create_ai_prediction

class MLPipeline:
    """
    Main ML Pipeline for MNTRK system.
    Orchestrates different ML models for various prediction tasks.
    """
    
    def __init__(self):
        self.habitat_predictor = HabitatPredictor()
        self.movement_predictor = MovementPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.models_loaded = False
        
    async def initialize(self):
        """Initialize and load pre-trained models."""
        try:
            await self.habitat_predictor.load_model()
            await self.movement_predictor.load_model()
            await self.anomaly_detector.load_model()
            self.models_loaded = True
            print("ML Pipeline initialized successfully")
        except Exception as e:
            print(f"Warning: Could not load pre-trained models: {e}")
            print("Models will be trained on first use")
    
    async def predict_habitat_suitability(self, environmental_data: Dict) -> Dict:
        """
        Predict habitat suitability based on environmental factors.
        
        Args:
            environmental_data: Dict containing temperature, rainfall, vegetation_index, etc.
            
        Returns:
            Dict with suitability_score and risk_factors
        """
        try:
            result = await self.habitat_predictor.predict(environmental_data)
            
            # Store prediction in database
            prediction_data = {
                'prediction_type': 'habitat_suitability',
                'input_data': environmental_data,
                'prediction_result': result,
                'model_version': self.habitat_predictor.version,
                'confidence_score': result.get('confidence', 0.0)
            }
            
            prediction_id = await create_ai_prediction(prediction_data)
            result['prediction_id'] = prediction_id
            
            return result
            
        except Exception as e:
            raise Exception(f"Habitat prediction failed: {str(e)}")
    
    async def predict_movement_patterns(self, location_data: Dict, time_horizon: int = 30) -> Dict:
        """
        Predict Mastomys movement patterns.
        
        Args:
            location_data: Current location and environmental context
            time_horizon: Prediction horizon in days
            
        Returns:
            Dict with predicted movements and probabilities
        """
        try:
            result = await self.movement_predictor.predict(location_data, time_horizon)
            
            # Store prediction in database
            prediction_data = {
                'prediction_type': 'movement_patterns',
                'input_data': {**location_data, 'time_horizon': time_horizon},
                'prediction_result': result,
                'model_version': self.movement_predictor.version,
                'confidence_score': result.get('confidence', 0.0)
            }
            
            prediction_id = await create_ai_prediction(prediction_data)
            result['prediction_id'] = prediction_id
            
            return result
            
        except Exception as e:
            raise Exception(f"Movement prediction failed: {str(e)}")
    
    async def detect_anomalies(self, sensor_data: List[Dict]) -> Dict:
        """
        Detect anomalies in environmental sensor data.
        
        Args:
            sensor_data: List of sensor readings with timestamps
            
        Returns:
            Dict with anomaly scores and flagged data points
        """
        try:
            result = await self.anomaly_detector.detect(sensor_data)
            
            # Store prediction in database
            prediction_data = {
                'prediction_type': 'anomaly_detection',
                'input_data': {'sensor_data_count': len(sensor_data)},
                'prediction_result': result,
                'model_version': self.anomaly_detector.version,
                'confidence_score': result.get('avg_anomaly_score', 0.0)
            }
            
            prediction_id = await create_ai_prediction(prediction_data)
            result['prediction_id'] = prediction_id
            
            return result
            
        except Exception as e:
            raise Exception(f"Anomaly detection failed: {str(e)}")
    
    async def train_models(self, training_data: Dict) -> Dict:
        """
        Train or retrain ML models with new data.
        
        Args:
            training_data: Dict containing training datasets for different models
            
        Returns:
            Dict with training results and model performance metrics
        """
        results = {}
        
        try:
            # Train habitat predictor
            if 'habitat_data' in training_data:
                habitat_results = await self.habitat_predictor.train(training_data['habitat_data'])
                results['habitat_predictor'] = habitat_results
            
            # Train movement predictor
            if 'movement_data' in training_data:
                movement_results = await self.movement_predictor.train(training_data['movement_data'])
                results['movement_predictor'] = movement_results
            
            # Train anomaly detector
            if 'sensor_data' in training_data:
                anomaly_results = await self.anomaly_detector.train(training_data['sensor_data'])
                results['anomaly_detector'] = anomaly_results
            
            # Store training results
            prediction_data = {
                'prediction_type': 'model_training',
                'input_data': {'datasets': list(training_data.keys())},
                'prediction_result': results,
                'model_version': 'training_session',
                'confidence_score': 1.0
            }
            
            prediction_id = await create_ai_prediction(prediction_data)
            results['training_session_id'] = prediction_id
            
            return results
            
        except Exception as e:
            raise Exception(f"Model training failed: {str(e)}")
    
    async def get_model_status(self) -> Dict:
        """Get status and performance metrics of all models."""
        return {
            'models_loaded': self.models_loaded,
            'habitat_predictor': await self.habitat_predictor.get_status(),
            'movement_predictor': await self.movement_predictor.get_status(),
            'anomaly_detector': await self.anomaly_detector.get_status(),
            'last_updated': datetime.now().isoformat()
        }

# Global pipeline instance
pipeline = MLPipeline()

async def get_pipeline() -> MLPipeline:
    """Get the global ML pipeline instance."""
    if not pipeline.models_loaded:
        await pipeline.initialize()
    return pipeline
