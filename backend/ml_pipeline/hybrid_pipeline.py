import pandas as pd
import numpy as np
import joblib
import logging
import asyncio
from datetime import datetime, timedelta
import os
from shared import firebase_config
from sqlalchemy.future import select
from sqlalchemy import text
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss
from firebase_admin import firestore, storage

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Hybrid-Training")

class HybridTrainingPipeline:
    """
    Sovereign Hybrid Training Pipeline
    Combines live Firestore data with historical Neon PostgreSQL data
    for optimal model training with both adaptive and stable patterns.
    """
    
    def __init__(self, firestore_window_days=30):
        """
        Initialize the hybrid training pipeline.
        
        Args:
            firestore_window_days: Number of days of recent data to pull from Firestore
        """
        self.db = firebase_config.db
        self.firestore_window_days = firestore_window_days
        self.bucket = storage.bucket()
        
    async def fetch_firestore_data(self, collection, filter_field=None):
        """
        Fetch recent adaptive data from Firestore.
        
        Args:
            collection: Firestore collection name
            filter_field: Field to use for time filtering
            
        Returns:
            DataFrame with recent Firestore data
        """
        logger.info(f"Fetching live adaptive data from Firestore ({collection})...")
        
        try:
            # Calculate cutoff date for recent data
            cutoff_date = datetime.now() - timedelta(days=self.firestore_window_days)
            
            if filter_field:
                # Query with time filter
                query = self.db.collection(collection).where(
                    filter_field, '>=', cutoff_date
                )
                docs = query.stream()
            else:
                # Get all documents (will filter later if possible)
                docs = self.db.collection(collection).stream()
            
            # Convert to list of dicts
            data = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id
                data.append(item)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Apply time filter if field exists but wasn't used in query
            if filter_field and filter_field in df.columns:
                df[filter_field] = pd.to_datetime(df[filter_field])
                df = df[df[filter_field] >= cutoff_date]
            
            logger.info(f"Retrieved {len(df)} records from Firestore {collection}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Firestore data: {e}")
            return pd.DataFrame()
    
    async def fetch_neon_data(self, table_name, db_session):
        """
        Fetch historical archive data from Neon PostgreSQL.
        
        Args:
            table_name: PostgreSQL table name
            db_session: SQLAlchemy async session
            
        Returns:
            DataFrame with historical data
        """
        logger.info(f"Fetching historical archive from Neon ({table_name})...")
        
        try:
            # Query all data from the specified table
            query = text(f"SELECT * FROM {table_name}")
            result = await db_session.execute(query)
            rows = result.fetchall()
            
            if not rows:
                logger.warning(f"No data found in Neon table {table_name}")
                return pd.DataFrame()
            
            # Get column names from result
            columns = result.keys()
            
            # Create DataFrame
            neon_df = pd.DataFrame(rows, columns=columns)
            logger.info(f"Retrieved {len(neon_df)} historical records from Neon {table_name}")
            return neon_df
            
        except Exception as e:
            logger.error(f"Error fetching Neon data: {e}")
            return pd.DataFrame()
    
    def merge_datasets(self, df_live, df_historical, key_columns=None, weight_recent=2.0):
        """
        Merge live and historical datasets with intelligent fusion.
        
        Args:
            df_live: DataFrame with recent Firestore data
            df_historical: DataFrame with historical Neon data
            key_columns: Columns to use for deduplication
            weight_recent: Weight factor for recent data (for sampling)
            
        Returns:
            Merged DataFrame
        """
        logger.info("Merging live + historical data...")
        
        if df_live.empty and df_historical.empty:
            logger.error("Both datasets are empty, cannot merge")
            return pd.DataFrame()
        
        if df_live.empty:
            logger.warning("Live dataset is empty, using only historical data")
            return df_historical
        
        if df_historical.empty:
            logger.warning("Historical dataset is empty, using only live data")
            return df_live
        
        try:
            # Ensure column compatibility
            common_columns = set(df_live.columns).intersection(set(df_historical.columns))
            if not common_columns:
                logger.error("No common columns between datasets")
                # Return the dataset with more rows
                return df_live if len(df_live) > len(df_historical) else df_historical
            
            # Use only common columns
            df_live = df_live[list(common_columns)]
            df_historical = df_historical[list(common_columns)]
            
            # Merge datasets
            combined = pd.concat([df_live, df_historical], ignore_index=True)
            
            # Deduplicate if key columns provided
            if key_columns:
                before_dedup = len(combined)
                combined = combined.drop_duplicates(subset=key_columns)
                logger.info(f"Removed {before_dedup - len(combined)} duplicate records")
            
            # Handle missing values
            combined.fillna(combined.mean(numeric_only=True), inplace=True)
            
            # Apply weighting through sampling if needed
            if weight_recent > 1.0 and len(df_live) > 0:
                # Sample recent data with higher weight
                recent_sample = df_live.sample(
                    n=min(len(df_live), int(len(df_live) * weight_recent)), 
                    replace=True
                )
                # Combine with original merged data
                combined = pd.concat([combined, recent_sample], ignore_index=True)
                logger.info(f"Applied weight {weight_recent} to recent data")
            
            logger.info(f"Final merged dataset: {len(combined)} records")
            return combined
            
        except Exception as e:
            logger.error(f"Error merging datasets: {e}")
            # Return the dataset with more rows as fallback
            return df_live if len(df_live) > len(df_historical) else df_historical
    
    async def train_hybrid_model(self, df, model_type, features, label, hyperparams=None):
        """
        Train model using the hybrid dataset.
        
        Args:
            df: Merged DataFrame with training data
            model_type: Type of model to train ('rf' or 'gb')
            features: List of feature column names
            label: Target column name
            hyperparams: Optional hyperparameters dict
            
        Returns:
            Tuple of (model_path, metrics)
        """
        logger.info(f"Training hybrid fusion {model_type} model...")
        
        try:
            # Ensure all required columns exist
            missing_features = [f for f in features if f not in df.columns]
            if missing_features:
                logger.error(f"Missing features in dataset: {missing_features}")
                return None, {"error": f"Missing features: {missing_features}"}
            
            if label not in df.columns:
                logger.error(f"Label column '{label}' not found in dataset")
                return None, {"error": f"Missing label column: {label}"}
            
            # Prepare data
            X = df[features]
            y = df[label]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Set default hyperparameters if not provided
            if not hyperparams:
                hyperparams = {}
            
            # Create model based on type
            if model_type.lower() == 'rf':
                model = RandomForestClassifier(
                    n_estimators=hyperparams.get('n_estimators', 200),
                    max_depth=hyperparams.get('max_depth', 8),
                    random_state=42
                )
            elif model_type.lower() == 'gb':
                model = GradientBoostingClassifier(
                    n_estimators=hyperparams.get('n_estimators', 100),
                    max_depth=hyperparams.get('max_depth', 5),
                    learning_rate=hyperparams.get('learning_rate', 0.1),
                    random_state=42
                )
            else:
                logger.error(f"Unknown model type: {model_type}")
                return None, {"error": f"Unknown model type: {model_type}"}
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            metrics = {
                'accuracy': float(accuracy_score(y_test, y_pred)),
                'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            }
            
            if y_proba is not None:
                metrics['loss'] = float(log_loss(y_test, y_proba))
            
            # Save model locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"{model_type}_{timestamp}.joblib"
            local_path = f"/tmp/{model_filename}"
            joblib.dump(model, local_path)
            
            # Upload to Firebase Storage
            storage_path = f"models/{model_filename}"
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(local_path)
            
            # Update model registry in Firestore
            model_doc = {
                'model_type': model_type,
                'features': features,
                'label': label,
                'hyperparams': hyperparams,
                'metrics': metrics,
                'storage_path': storage_path,
                'training_samples': len(df),
                'created_at': firestore.SERVER_TIMESTAMP,
                'status': 'active'
            }
            
            self.db.collection('model_registry').document(model_filename).set(model_doc)
            
            logger.info(f"✅ Hybrid model trained and registered: {metrics}")
            return storage_path, metrics
            
        except Exception as e:
            logger.error(f"Error training hybrid model: {e}")
            return None, {"error": str(e)}
    
    async def execute_hybrid_training(self, db_session, model_config):
        """
        Execute the full hybrid training pipeline.
        
        Args:
            db_session: SQLAlchemy async session
            model_config: Dict with model configuration
            
        Returns:
            Tuple of (model_path, metrics)
        """
        try:
            # Extract configuration
            firestore_collection = model_config.get('firestore_collection', 'training_data')
            neon_table = model_config.get('neon_table', 'ecological_training_data')
            time_field = model_config.get('time_field', 'created_at')
            model_type = model_config.get('model_type', 'rf')
            features = model_config.get('features', [])
            label = model_config.get('label', 'outbreak_risk')
            key_columns = model_config.get('key_columns', None)
            hyperparams = model_config.get('hyperparams', {})
            
            # Fetch data from both sources
            df_live = await self.fetch_firestore_data(firestore_collection, time_field)
            df_historical = await self.fetch_neon_data(neon_table, db_session)
            
            # Merge datasets
            merged_df = self.merge_datasets(df_live, df_historical, key_columns)
            
            if merged_df.empty:
                logger.error("No data available for training")
                return None, {"error": "No data available for training"}
            
            # Train model
            model_path, metrics = await self.train_hybrid_model(
                merged_df, model_type, features, label, hyperparams
            )
            
            return model_path, metrics
            
        except Exception as e:
            logger.error(f"Error executing hybrid training: {e}")
            return None, {"error": str(e)}

# Singleton instance
hybrid_pipeline = HybridTrainingPipeline()
