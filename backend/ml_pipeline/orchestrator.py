import logging
import asyncio
from datetime import datetime, timedelta
import os
import json
from firebase_admin import firestore
from shared import firebase_config
from shared.database import get_session
from .hybrid_pipeline import hybrid_pipeline

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sovereign-Orchestrator")

class SovereignOrchestrator:
    """
    Sovereign Orchestrator for the MNTRK ML Pipeline
    Manages and coordinates all training activities across the system.
    """
    
    def __init__(self):
        """Initialize the sovereign orchestrator."""
        self.db = firebase_config.db
        self.training_configs = {
            'habitat': {
                'firestore_collection': 'habitat_analyses',
                'neon_table': 'mntrk.habitat_analyses',
                'time_field': 'analysis_timestamp',
                'model_type': 'rf',
                'features': [
                    'latitude', 'longitude', 'temperature', 'rainfall', 
                    'humidity', 'vegetation_index', 'soil_moisture', 'elevation'
                ],
                'label': 'suitability_score',
                'key_columns': ['latitude', 'longitude'],
                'hyperparams': {
                    'n_estimators': 200,
                    'max_depth': 8
                }
            },
            'movement': {
                'firestore_collection': 'detection_patterns',
                'neon_table': 'mntrk.detection_patterns',
                'time_field': 'detection_timestamp',
                'model_type': 'gb',
                'features': [
                    'latitude', 'longitude', 'confidence_score',
                    'environmental_temperature', 'environmental_humidity'
                ],
                'label': 'movement_direction',
                'key_columns': ['latitude', 'longitude', 'detection_timestamp'],
                'hyperparams': {
                    'n_estimators': 150,
                    'max_depth': 6,
                    'learning_rate': 0.1
                }
            },
            'anomaly': {
                'firestore_collection': 'environmental_data',
                'neon_table': 'mntrk.environmental_data',
                'time_field': 'measurement_timestamp',
                'model_type': 'rf',
                'features': [
                    'temperature', 'rainfall', 'humidity', 
                    'vegetation_index', 'soil_moisture'
                ],
                'label': 'is_anomaly',
                'key_columns': ['latitude', 'longitude', 'measurement_timestamp'],
                'hyperparams': {
                    'n_estimators': 300,
                    'max_depth': 10
                }
            }
        }
    
    async def check_training_schedule(self):
        """
        Check if any models are due for scheduled training.
        
        Returns:
            Dict of model types that need training
        """
        try:
            schedule_ref = self.db.collection('training_schedule').document('schedule')
            schedule_doc = schedule_ref.get()
            
            if not schedule_doc.exists:
                logger.warning("No training schedule found")
                return {}
            
            schedule = schedule_doc.to_dict()
            now = datetime.now()
            
            training_needed = {}
            
            for model_type, config in schedule.items():
                last_trained = config.get('last_trained')
                frequency_days = config.get('frequency_days', 7)
                
                if not last_trained:
                    training_needed[model_type] = True
                    continue
                
                # Convert Firestore timestamp to datetime
                if hasattr(last_trained, 'timestamp'):
                    last_trained = datetime.fromtimestamp(last_trained.timestamp())
                
                # Check if training is due
                if now - last_trained > timedelta(days=frequency_days):
                    training_needed[model_type] = True
            
            return training_needed
            
        except Exception as e:
            logger.error(f"Error checking training schedule: {e}")
            return {}
    
    async def update_training_schedule(self, model_type):
        """
        Update the last trained timestamp for a model.
        
        Args:
            model_type: Type of model that was trained
        """
        try:
            schedule_ref = self.db.collection('training_schedule').document('schedule')
            
            # Update the specific model's last_trained timestamp
            schedule_ref.update({
                f"{model_type}.last_trained": firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Updated training schedule for {model_type}")
            
        except Exception as e:
            logger.error(f"Error updating training schedule: {e}")
    
    async def execute_training(self, model_type):
        """
        Execute training for a specific model type.
        
        Args:
            model_type: Type of model to train
            
        Returns:
            Training results
        """
        try:
            if model_type not in self.training_configs:
                logger.error(f"Unknown model type: {model_type}")
                return {"error": f"Unknown model type: {model_type}"}
            
            config = self.training_configs[model_type]
            
            # Get database session
            async for session in get_session():
                # Execute hybrid training
                model_path, metrics = await hybrid_pipeline.execute_hybrid_training(
                    session, config
                )
                
                if model_path:
                    # Update training schedule
                    await self.update_training_schedule(model_type)
                    
                    # Log success
                    logger.info(f"Successfully trained {model_type} model: {metrics}")
                    
                    return {
                        "status": "success",
                        "model_type": model_type,
                        "model_path": model_path,
                        "metrics": metrics
                    }
                else:
                    logger.error(f"Failed to train {model_type} model: {metrics}")
                    return {
                        "status": "error",
                        "model_type": model_type,
                        "error": metrics.get("error", "Unknown error")
                    }
                
        except Exception as e:
            logger.error(f"Error executing training for {model_type}: {e}")
            return {
                "status": "error",
                "model_type": model_type,
                "error": str(e)
            }
    
    async def run_scheduled_training(self):
        """
        Run scheduled training for all models that need it.
        
        Returns:
            Dict with training results
        """
        try:
            # Check which models need training
            training_needed = await self.check_training_schedule()
            
            if not training_needed:
                logger.info("No models due for scheduled training")
                return {"status": "no_training_needed"}
            
            # Train each model that needs it
            results = {}
            for model_type in training_needed:
                logger.info(f"Starting scheduled training for {model_type}")
                result = await self.execute_training(model_type)
                results[model_type] = result
            
            return {
                "status": "completed",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error running scheduled training: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_full_training_cycle(self):
        """
        Run a full training cycle for all models.
        
        Returns:
            Dict with training results
        """
        try:
            results = {}
            
            for model_type in self.training_configs:
                logger.info(f"Starting full training cycle for {model_type}")
                result = await self.execute_training(model_type)
                results[model_type] = result
            
            return {
                "status": "completed",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error running full training cycle: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Singleton instance
orchestrator = SovereignOrchestrator()

# Function to be called by Firebase triggers or scheduled jobs
async def trigger_scheduled_training():
    """Check schedule and run training if needed."""
    try:
        return await orchestrator.run_scheduled_training()
    except Exception as e:
        logger.error(f"Error in scheduled training trigger: {e}")
        return {"status": "error", "error": str(e)}

# Function to force full training cycle
async def trigger_full_training():
    """Force a full training cycle for all models."""
    try:
        return await orchestrator.run_full_training_cycle()
    except Exception as e:
        logger.error(f"Error in full training trigger: {e}")
        return {"status": "error", "error": str(e)}
