import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from firebase.client import get_firestore, get_storage
from firebase.detection_patterns import DetectionPatternsService
from firebase.habitat_models import HabitatModelsService
from firebase.predictive_analytics import PredictiveAnalyticsService
from .models.habitat_predictor import HabitatPredictor
from .models.movement_predictor import MovementPredictor
from .models.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)

class TrainingManager:
    """
    Manages ML model training triggered by Firebase events.
    Handles data collection, preprocessing, and model updates.
    """
    
    def __init__(self):
        self.db = get_firestore()
        self.storage = get_storage()
        self.detection_service = DetectionPatternsService()
        self.habitat_service = HabitatModelsService()
        self.analytics_service = PredictiveAnalyticsService()
        
        # Training thresholds
        self.min_training_samples = 100
        self.retrain_threshold = 50  # New samples needed to trigger retraining
        
    async def check_training_trigger(self) -> Dict[str, bool]:
        """
        Check if any models need retraining based on new data.
        
        Returns:
            Dict indicating which models need retraining
        """
        triggers = {
            'habitat_predictor': False,
            'movement_predictor': False,
            'anomaly_detector': False
        }
        
        try:
            # Check habitat predictor
            habitat_count = await self._get_new_data_count('habitat_analyses')
            if habitat_count >= self.retrain_threshold:
                triggers['habitat_predictor'] = True
                logger.info(f"Habitat predictor needs retraining: {habitat_count} new samples")
            
            # Check movement predictor
            detection_count = await self._get_new_data_count('detection_patterns')
            if detection_count >= self.retrain_threshold:
                triggers['movement_predictor'] = True
                logger.info(f"Movement predictor needs retraining: {detection_count} new samples")
            
            # Check anomaly detector
            env_count = await self._get_new_data_count('environmental_data')
            if env_count >= self.retrain_threshold:
                triggers['anomaly_detector'] = True
                logger.info(f"Anomaly detector needs retraining: {env_count} new samples")
                
        except Exception as e:
            logger.error(f"Error checking training triggers: {e}")
            
        return triggers
    
    async def _get_new_data_count(self, collection: str) -> int:
        """Get count of new data since last training."""
        try:
            # Get last training timestamp from model metadata
            model_meta_ref = self.db.collection('ml_models').document(f'{collection}_model')
            model_meta = model_meta_ref.get()
            
            if model_meta.exists:
                last_trained = model_meta.to_dict().get('last_trained')
                if last_trained:
                    # Count documents created after last training
                    query = self.db.collection(collection).where('created_at', '>', last_trained)
                    docs = query.stream()
                    return len(list(docs))
            
            # If no training history, count all documents
            docs = self.db.collection(collection).stream()
            return len(list(docs))
            
        except Exception as e:
            logger.error(f"Error getting new data count for {collection}: {e}")
            return 0
    
    async def collect_training_data(self, data_type: str) -> pd.DataFrame:
        """
        Collect training data from Firebase for specific model type.
        
        Args:
            data_type: Type of data ('habitat', 'movement', 'anomaly')
            
        Returns:
            DataFrame with training data
        """
        try:
            if data_type == 'habitat':
                return await self._collect_habitat_data()
            elif data_type == 'movement':
                return await self._collect_movement_data()
            elif data_type == 'anomaly':
                return await self._collect_anomaly_data()
            else:
                raise ValueError(f"Unknown data type: {data_type}")
                
        except Exception as e:
            logger.error(f"Error collecting training data for {data_type}: {e}")
            raise
    
    async def _collect_habitat_data(self) -> pd.DataFrame:
        """Collect habitat analysis data for training."""
        try:
            # Get habitat analyses from Firebase
            habitat_docs = self.db.collection('habitat_analyses').stream()
            habitat_data = []
            
            for doc in habitat_docs:
                data = doc.to_dict()
                
                # Extract features for training
                features = {
                    'latitude': data.get('latitude', 0.0),
                    'longitude': data.get('longitude', 0.0),
                    'temperature': data.get('environmental_data', {}).get('temperature', 0.0),
                    'rainfall': data.get('environmental_data', {}).get('rainfall', 0.0),
                    'humidity': data.get('environmental_data', {}).get('humidity', 0.0),
                    'vegetation_index': data.get('environmental_data', {}).get('vegetation_index', 0.0),
                    'soil_moisture': data.get('environmental_data', {}).get('soil_moisture', 0.0),
                    'elevation': data.get('environmental_data', {}).get('elevation', 0.0),
                    'suitability_score': data.get('suitability_score', 0.0),  # Target variable
                    'created_at': data.get('created_at')
                }
                
                habitat_data.append(features)
            
            df = pd.DataFrame(habitat_data)
            logger.info(f"Collected {len(df)} habitat training samples")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting habitat data: {e}")
            raise
    
    async def _collect_movement_data(self) -> pd.DataFrame:
        """Collect detection pattern data for movement prediction training."""
        try:
            # Get detection patterns from Firebase
            detection_docs = self.db.collection('detection_patterns').stream()
            movement_data = []
            
            for doc in detection_docs:
                data = doc.to_dict()
                
                # Extract features for movement prediction
                features = {
                    'latitude': data.get('latitude', 0.0),
                    'longitude': data.get('longitude', 0.0),
                    'detection_timestamp': data.get('detection_timestamp'),
                    'confidence_score': data.get('confidence_score', 0.0),
                    'detection_method': data.get('detection_method', 'unknown'),
                    'environmental_temperature': data.get('environmental_context', {}).get('temperature', 0.0),
                    'environmental_humidity': data.get('environmental_context', {}).get('humidity', 0.0),
                    'time_of_day': self._extract_time_features(data.get('detection_timestamp')),
                    'season': self._extract_season(data.get('detection_timestamp')),
                    'created_at': data.get('created_at')
                }
                
                movement_data.append(features)
            
            df = pd.DataFrame(movement_data)
            logger.info(f"Collected {len(df)} movement training samples")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting movement data: {e}")
            raise
    
    async def _collect_anomaly_data(self) -> pd.DataFrame:
        """Collect environmental data for anomaly detection training."""
        try:
            # Get environmental data from Firebase
            env_docs = self.db.collection('environmental_data').stream()
            anomaly_data = []
            
            for doc in env_docs:
                data = doc.to_dict()
                
                # Extract features for anomaly detection
                features = {
                    'latitude': data.get('latitude', 0.0),
                    'longitude': data.get('longitude', 0.0),
                    'temperature': data.get('temperature', 0.0),
                    'rainfall': data.get('rainfall', 0.0),
                    'humidity': data.get('humidity', 0.0),
                    'vegetation_index': data.get('vegetation_index', 0.0),
                    'soil_moisture': data.get('soil_moisture', 0.0),
                    'elevation': data.get('elevation', 0.0),
                    'measurement_timestamp': data.get('measurement_timestamp'),
                    'data_source': data.get('data_source', 'unknown'),
                    'created_at': data.get('created_at')
                }
                
                anomaly_data.append(features)
            
            df = pd.DataFrame(anomaly_data)
            logger.info(f"Collected {len(df)} anomaly detection training samples")
            return df
            
        except Exception as e:
            logger.error(f"Error collecting anomaly data: {e}")
            raise
    
    def _extract_time_features(self, timestamp) -> int:
        """Extract hour of day from timestamp."""
        if timestamp:
            try:
                if hasattr(timestamp, 'hour'):
                    return timestamp.hour
                # Handle Firestore timestamp
                return timestamp.hour if hasattr(timestamp, 'hour') else 12
            except:
                return 12
        return 12
    
    def _extract_season(self, timestamp) -> str:
        """Extract season from timestamp."""
        if timestamp:
            try:
                month = timestamp.month if hasattr(timestamp, 'month') else 6
                if month in [12, 1, 2]:
                    return 'dry_season'
                elif month in [3, 4, 5]:
                    return 'transition'
                elif month in [6, 7, 8]:
                    return 'wet_season'
                else:
                    return 'late_wet'
            except:
                return 'unknown'
        return 'unknown'
    
    async def train_model(self, model_type: str) -> Dict:
        """
        Train a specific model with latest data.
        
        Args:
            model_type: Type of model to train ('habitat', 'movement', 'anomaly')
            
        Returns:
            Training results and metrics
        """
        try:
            logger.info(f"Starting training for {model_type} model")
            
            # Collect training data
            training_data = await self.collect_training_data(model_type)
            
            if len(training_data) < self.min_training_samples:
                raise ValueError(f"Insufficient training data: {len(training_data)} < {self.min_training_samples}")
            
            # Train the appropriate model
            if model_type == 'habitat':
                predictor = HabitatPredictor()
                results = await predictor.train(training_data)
            elif model_type == 'movement':
                predictor = MovementPredictor()
                results = await predictor.train(training_data)
            elif model_type == 'anomaly':
                detector = AnomalyDetector()
                results = await detector.train(training_data)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Update model metadata in Firebase
            await self._update_model_metadata(model_type, results)
            
            logger.info(f"Training completed for {model_type}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error training {model_type} model: {e}")
            raise
    
    async def _update_model_metadata(self, model_type: str, results: Dict):
        """Update model metadata in Firebase after training."""
        try:
            model_meta_ref = self.db.collection('ml_models').document(f'{model_type}_model')
            
            metadata = {
                'model_type': model_type,
                'last_trained': datetime.now(),
                'version': results.get('version', '1.0.0'),
                'accuracy': results.get('accuracy', 0.0),
                'precision': results.get('precision', 0.0),
                'recall': results.get('recall', 0.0),
                'f1_score': results.get('f1_score', 0.0),
                'training_samples': results.get('training_samples', 0),
                'status': 'trained',
                'new_data_count': 0  # Reset counter after training
            }
            
            model_meta_ref.set(metadata)
            logger.info(f"Updated metadata for {model_type} model")
            
        except Exception as e:
            logger.error(f"Error updating model metadata: {e}")
    
    async def download_training_files(self, file_paths: List[str]) -> List[str]:
        """
        Download training files from Firebase Storage.
        
        Args:
            file_paths: List of file paths in Firebase Storage
            
        Returns:
            List of local file paths
        """
        local_files = []
        
        try:
            for file_path in file_paths:
                # Download file from Firebase Storage
                blob = self.storage.blob(file_path)
                
                if not blob.exists():
                    logger.warning(f"File not found in storage: {file_path}")
                    continue
                
                # Create local file path
                local_path = f"/tmp/{file_path.split('/')[-1]}"
                
                # Download file
                blob.download_to_filename(local_path)
                local_files.append(local_path)
                
                logger.info(f"Downloaded training file: {file_path} -> {local_path}")
            
            return local_files
            
        except Exception as e:
            logger.error(f"Error downloading training files: {e}")
            raise

# Global training manager instance
training_manager = TrainingManager()

async def trigger_training_check():
    """Function to be called by Firebase triggers or scheduled jobs."""
    try:
        triggers = await training_manager.check_training_trigger()
        
        for model_type, should_train in triggers.items():
            if should_train:
                logger.info(f"Triggering training for {model_type}")
                await training_manager.train_model(model_type.replace('_predictor', '').replace('_detector', ''))
                
    except Exception as e:
        logger.error(f"Error in training trigger check: {e}")
