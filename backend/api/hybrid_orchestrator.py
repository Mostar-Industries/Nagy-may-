"""
MNTRK Sovereign Observatory - Hybrid ML Orchestrator
Coordinates ML training across Firestore, Neon, and Synthetic data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

from shared.database import get_db, query_recent_detections, create_ai_prediction
from shared.neon_database import get_neon_sql, query_historical_data
from shared.synthetic_data import generate_synthetic_training_data
from symbolic_engine.engine import SymbolicReasoningEngine

logger = logging.getLogger("Hybrid-Orchestrator")

class HybridMLOrchestrator:
    """
    Orchestrates hybrid machine learning across multiple data sources:
    - Firestore (real-time data)
    - Neon PostgreSQL (historical archive)
    - MostlyAI (synthetic data augmentation)
    - Symbolic reasoning integration
    """
    
    def __init__(self):
        self.model = None
        self.symbolic_engine = SymbolicReasoningEngine()
        self.model_version = "1.0.0"
        self.last_training = None
        
    async def execute_hybrid_training(self) -> Dict:
        """
        Execute complete hybrid training pipeline.
        
        Returns:
            Dict with training metrics and model performance
        """
        try:
            logger.info("🚀 Starting Hybrid ML Training Pipeline")
            
            # Step 1: Collect data from all sources
            training_data = await self._collect_hybrid_data()
            
            # Step 2: Prepare and merge datasets
            merged_dataset = await self._prepare_training_dataset(training_data)
            
            # Step 3: Train ML model
            model_metrics = await self._train_ml_model(merged_dataset)
            
            # Step 4: Integrate symbolic reasoning
            symbolic_rules = await self._generate_symbolic_rules(merged_dataset)
            
            # Step 5: Create hybrid inference pipeline
            hybrid_model = await self._create_hybrid_model(model_metrics, symbolic_rules)
            
            # Step 6: Validate and save model
            validation_results = await self._validate_hybrid_model(hybrid_model, merged_dataset)
            
            # Step 7: Store training results
            training_record = await self._store_training_results(validation_results)
            
            logger.info("✅ Hybrid ML Training Pipeline Completed Successfully")
            
            return {
                "status": "success",
                "training_id": training_record,
                "model_version": self.model_version,
                "data_sources": {
                    "firestore_records": training_data["firestore_count"],
                    "neon_records": training_data["neon_count"], 
                    "synthetic_records": training_data["synthetic_count"]
                },
                "model_performance": validation_results,
                "symbolic_rules_count": len(symbolic_rules),
                "training_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hybrid training failed: {e}")
            raise Exception(f"Hybrid ML training failed: {str(e)}")
    
    async def _collect_hybrid_data(self) -> Dict:
        """Collect data from all sources: Firestore, Neon, and Synthetic."""
        logger.info("📊 Collecting data from hybrid sources")
        
        # Collect from Firestore (last 30 days)
        firestore_data = await self._collect_firestore_data()
        
        # Collect from Neon (historical archive)
        neon_data = await self._collect_neon_data()
        
        # Generate synthetic data for augmentation
        synthetic_data = await self._collect_synthetic_data()
        
        return {
            "firestore": firestore_data,
            "firestore_count": len(firestore_data),
            "neon": neon_data,
            "neon_count": len(neon_data),
            "synthetic": synthetic_data,
            "synthetic_count": len(synthetic_data)
        }
    
    async def _collect_firestore_data(self) -> List[Dict]:
        """Collect recent data from Firestore."""
        try:
            # Get recent detection patterns
            recent_detections = query_recent_detections(limit=1000)
            
            # Convert to training format
            training_records = []
            for detection in recent_detections:
                record = {
                    "latitude": detection.get("latitude", 0),
                    "longitude": detection.get("longitude", 0),
                    "detection_count": detection.get("detection_count", 0),
                    "temperature": detection.get("environmental_context", {}).get("temperature", 25),
                    "rainfall": detection.get("environmental_context", {}).get("rainfall", 0),
                    "vegetation_index": detection.get("environmental_context", {}).get("vegetation_index", 0.5),
                    "season": self._extract_season(detection.get("detection_timestamp")),
                    "risk_level": detection.get("risk_assessment", {}).get("level", "medium"),
                    "source": "firestore"
                }
                training_records.append(record)
            
            logger.info(f"📊 Collected {len(training_records)} records from Firestore")
            return training_records
            
        except Exception as e:
            logger.warning(f"Firestore data collection failed: {e}")
            return []
    
    async def _collect_neon_data(self) -> List[Dict]:
        """Collect historical data from Neon PostgreSQL."""
        try:
            sql = get_neon_sql()
            
            # Query historical detection data
            query = """
            SELECT 
                latitude, longitude, detection_count,
                temperature, rainfall, vegetation_index,
                season, risk_level, created_at
            FROM detection_patterns 
            WHERE created_at >= NOW() - INTERVAL '1 year'
            ORDER BY created_at DESC
            LIMIT 5000
            """
            
            result = sql(query)
            
            # Convert to training format
            training_records = []
            for row in result:
                record = {
                    "latitude": row[0],
                    "longitude": row[1], 
                    "detection_count": row[2],
                    "temperature": row[3],
                    "rainfall": row[4],
                    "vegetation_index": row[5],
                    "season": row[6],
                    "risk_level": row[7],
                    "source": "neon"
                }
                training_records.append(record)
            
            logger.info(f"📊 Collected {len(training_records)} records from Neon")
            return training_records
            
        except Exception as e:
            logger.warning(f"Neon data collection failed: {e}")
            return []
    
    async def _collect_synthetic_data(self) -> List[Dict]:
        """Generate synthetic training data."""
        try:
            # Generate synthetic data for data augmentation
            synthetic_records = await generate_synthetic_training_data(count=2000)
            
            logger.info(f"📊 Generated {len(synthetic_records)} synthetic records")
            return synthetic_records
            
        except Exception as e:
            logger.warning(f"Synthetic data generation failed: {e}")
            return []
    
    async def _prepare_training_dataset(self, training_data: Dict) -> pd.DataFrame:
        """Merge and prepare training dataset."""
        logger.info("🔄 Preparing merged training dataset")
        
        # Combine all data sources
        all_records = []
        all_records.extend(training_data["firestore"])
        all_records.extend(training_data["neon"])
        all_records.extend(training_data["synthetic"])
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        
        if df.empty:
            raise Exception("No training data available")
        
        # Feature engineering
        df = self._engineer_features(df)
        
        # Encode categorical variables
        df = self._encode_categorical_features(df)
        
        logger.info(f"📊 Prepared dataset with {len(df)} records and {len(df.columns)} features")
        return df
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for ML training."""
        # Create interaction features
        df['temp_rainfall_interaction'] = df['temperature'] * df['rainfall']
        df['vegetation_temp_ratio'] = df['vegetation_index'] / (df['temperature'] + 1)
        
        # Create risk indicators
        df['high_detection_flag'] = (df['detection_count'] > df['detection_count'].quantile(0.75)).astype(int)
        df['optimal_temp_flag'] = ((df['temperature'] >= 20) & (df['temperature'] &lt;= 30)).astype(int)
        
        # Spatial features
        df['lat_abs'] = abs(df['latitude'])
        df['lon_abs'] = abs(df['longitude'])
        
        return df
    
    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features for ML training."""
        # Encode season
        season_mapping = {'dry': 0, 'wet': 1, 'transition': 2}
        df['season_encoded'] = df['season'].map(season_mapping).fillna(1)
        
        # Encode risk level as target variable
        risk_mapping = {'low': 0, 'medium': 1, 'high': 2}
        df['risk_target'] = df['risk_level'].map(risk_mapping).fillna(1)
        
        # Encode data source
        source_mapping = {'firestore': 0, 'neon': 1, 'synthetic': 2}
        df['source_encoded'] = df['source'].map(source_mapping).fillna(0)
        
        return df
    
    async def _train_ml_model(self, df: pd.DataFrame) -> Dict:
        """Train Random Forest model on merged dataset."""
        logger.info("🧠 Training Random Forest model")
        
        # Prepare features and target
        feature_columns = [
            'latitude', 'longitude', 'detection_count', 'temperature', 
            'rainfall', 'vegetation_index', 'season_encoded',
            'temp_rainfall_interaction', 'vegetation_temp_ratio',
            'high_detection_flag', 'optimal_temp_flag', 'source_encoded'
        ]
        
        X = df[feature_columns]
        y = df['risk_target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Feature importance
        feature_importance = dict(zip(feature_columns, self.model.feature_importances_))
        
        # Save model
        model_path = f"models/hybrid_model_{self.model_version}.joblib"
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, model_path)
        
        metrics = {
            "accuracy": accuracy,
            "feature_importance": feature_importance,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "model_path": model_path
        }
        
        logger.info(f"🎯 Model trained with accuracy: {accuracy:.3f}")
        return metrics
    
    async def _generate_symbolic_rules(self, df: pd.DataFrame) -> List[Dict]:
        """Generate symbolic reasoning rules from data patterns."""
        logger.info("🔎 Generating symbolic reasoning rules")
        
        # Initialize symbolic engine
        await self.symbolic_engine.initialize()
        
        # Analyze data patterns for rule generation
        rules = []
        
        # High risk temperature rule
        high_temp_threshold = df['temperature'].quantile(0.8)
        rules.append({
            "rule_id": "high_temperature_risk",
            "condition": f"temperature > {high_temp_threshold}",
            "action": "increase_risk_level",
            "confidence": 0.85
        })
        
        # High detection count rule
        high_detection_threshold = df['detection_count'].quantile(0.9)
        rules.append({
            "rule_id": "high_detection_risk", 
            "condition": f"detection_count > {high_detection_threshold}",
            "action": "increase_risk_level",
            "confidence": 0.90
        })
        
        # Seasonal risk rule
        rules.append({
            "rule_id": "wet_season_risk",
            "condition": "season == 'wet' AND rainfall > 100",
            "action": "increase_risk_level", 
            "confidence": 0.75
        })
        
        # Store rules in symbolic engine
        await self.symbolic_engine.load_rules(rules)
        
        logger.info(f"🔎 Generated {len(rules)} symbolic rules")
        return rules
    
    async def _create_hybrid_model(self, ml_metrics: Dict, symbolic_rules: List[Dict]) -> Dict:
        """Create hybrid model combining ML and symbolic reasoning."""
        logger.info("🔗 Creating hybrid ML + Symbolic model")
        
        hybrid_model = {
            "ml_component": {
                "model_type": "RandomForest",
                "model_path": ml_metrics["model_path"],
                "accuracy": ml_metrics["accuracy"],
                "feature_importance": ml_metrics["feature_importance"]
            },
            "symbolic_component": {
                "rules_count": len(symbolic_rules),
                "rules": symbolic_rules,
                "engine_version": self.symbolic_engine.version
            },
            "fusion_strategy": "weighted_ensemble",
            "ml_weight": 0.7,
            "symbolic_weight": 0.3,
            "version": self.model_version
        }
        
        return hybrid_model
    
    async def _validate_hybrid_model(self, hybrid_model: Dict, df: pd.DataFrame) -> Dict:
        """Validate hybrid model performance."""
        logger.info("✅ Validating hybrid model")
        
        # Sample validation data
        validation_sample = df.sample(min(100, len(df)))
        
        # Test ML component
        ml_predictions = []
        for _, row in validation_sample.iterrows():
            try:
                features = [
                    row['latitude'], row['longitude'], row['detection_count'],
                    row['temperature'], row['rainfall'], row['vegetation_index'],
                    row['season_encoded'], row['temp_rainfall_interaction'],
                    row['vegetation_temp_ratio'], row['high_detection_flag'],
                    row['optimal_temp_flag'], row['source_encoded']
                ]
                ml_pred = self.model.predict([features])[0]
                ml_predictions.append(ml_pred)
            except:
                ml_predictions.append(1)  # Default medium risk
        
        # Test symbolic component
        symbolic_predictions = []
        for _, row in validation_sample.iterrows():
            symbolic_pred = await self.symbolic_engine.evaluate_risk(row.to_dict())
            symbolic_predictions.append(symbolic_pred.get('risk_level', 1))
        
        # Calculate hybrid predictions
        hybrid_predictions = []
        ml_weight = hybrid_model["ml_weight"]
        symbolic_weight = hybrid_model["symbolic_weight"]
        
        for ml_pred, sym_pred in zip(ml_predictions, symbolic_predictions):
            hybrid_pred = (ml_weight * ml_pred) + (symbolic_weight * sym_pred)
            hybrid_predictions.append(round(hybrid_pred))
        
        # Calculate validation metrics
        actual_values = validation_sample['risk_target'].tolist()
        
        # Simple accuracy calculation
        correct_predictions = sum(1 for actual, pred in zip(actual_values, hybrid_predictions) if actual == pred)
        hybrid_accuracy = correct_predictions / len(actual_values) if actual_values else 0
        
        validation_results = {
            "hybrid_accuracy": hybrid_accuracy,
            "ml_accuracy": ml_metrics["accuracy"],
            "validation_samples": len(validation_sample),
            "prediction_distribution": {
                "low_risk": hybrid_predictions.count(0),
                "medium_risk": hybrid_predictions.count(1), 
                "high_risk": hybrid_predictions.count(2)
            }
        }
        
        logger.info(f"✅ Hybrid model validation accuracy: {hybrid_accuracy:.3f}")
        return validation_results
    
    async def _store_training_results(self, validation_results: Dict) -> str:
        """Store training results in database."""
        training_record = {
            "training_type": "hybrid_ml_symbolic",
            "model_version": self.model_version,
            "training_timestamp": datetime.now().isoformat(),
            "validation_results": validation_results,
            "status": "completed"
        }
        
        # Store in Firestore
        training_id = create_ai_prediction(training_record)
        
        self.last_training = datetime.now()
        logger.info(f"📊 Training results stored with ID: {training_id}")
        
        return training_id
    
    def _extract_season(self, timestamp_str: str) -> str:
        """Extract season from timestamp."""
        try:
            if not timestamp_str:
                return "transition"
            
            # Simple season extraction based on month
            month = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).month
            
            if month in [12, 1, 2]:
                return "dry"
            elif month in [6, 7, 8]:
                return "wet"
            else:
                return "transition"
        except:
            return "transition"

# Global orchestrator instance
hybrid_orchestrator = HybridMLOrchestrator()

async def execute_training() -> Dict:
    """Execute hybrid training pipeline."""
    return await hybrid_orchestrator.execute_hybrid_training()
