import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from typing import Dict, List, Any
from datetime import datetime

class HabitatPredictor:
    """
    Predicts habitat suitability for Mastomys Natalensis based on environmental factors.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'temperature', 'rainfall', 'vegetation_index', 
            'soil_moisture', 'elevation', 'humidity'
        ]
        self.version = "1.0.0"
        self.model_path = "models/habitat_predictor.joblib"
        self.scaler_path = "models/habitat_scaler.joblib"
        
    async def load_model(self):
        """Load pre-trained model and scaler."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print(f"Habitat predictor model loaded from {self.model_path}")
            else:
                print("No pre-trained habitat model found. Will train on first use.")
        except Exception as e:
            print(f"Error loading habitat model: {e}")
    
    async def save_model(self):
        """Save trained model and scaler."""
        try:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print(f"Habitat predictor model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving habitat model: {e}")
    
    def _prepare_features(self, data: Dict) -> np.ndarray:
        """Prepare feature vector from input data."""
        features = []
        for feature in self.feature_names:
            value = data.get(feature, 0.0)
            features.append(float(value))
        return np.array(features).reshape(1, -1)
    
    async def predict(self, environmental_data: Dict) -> Dict:
        """
        Predict habitat suitability.
        
        Args:
            environmental_data: Dict with environmental parameters
            
        Returns:
            Dict with suitability_score, confidence, and risk_factors
        """
        if self.model is None:
            # Use simple heuristic if no trained model
            return await self._heuristic_prediction(environmental_data)
        
        try:
            # Prepare features
            features = self._prepare_features(environmental_data)
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            suitability_score = self.model.predict(features_scaled)[0]
            
            # Calculate confidence (simplified)
            confidence = min(0.95, max(0.5, 1.0 - abs(suitability_score - 0.5) * 2))
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(environmental_data, suitability_score)
            
            return {
                'suitability_score': float(np.clip(suitability_score, 0, 1)),
                'confidence': float(confidence),
                'risk_factors': risk_factors,
                'model_version': self.version,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Habitat prediction error: {str(e)}")
    
    async def _heuristic_prediction(self, data: Dict) -> Dict:
        """Simple heuristic prediction when no trained model is available."""
        temp = data.get('temperature', 25)
        rainfall = data.get('rainfall', 100)
        vegetation = data.get('vegetation_index', 0.5)
        
        # Simple scoring based on known preferences
        temp_score = 1.0 if 20 <= temp <= 30 else max(0, 1 - abs(temp - 25) / 10)
        rain_score = 1.0 if 50 <= rainfall <= 200 else max(0, 1 - abs(rainfall - 125) / 100)
        veg_score = vegetation
        
        suitability = (temp_score + rain_score + veg_score) / 3
        
        risk_factors = []
        if temp < 15 or temp > 35:
            risk_factors.append("extreme_temperature")
        if rainfall < 30:
            risk_factors.append("drought_conditions")
        if rainfall > 300:
            risk_factors.append("flooding_risk")
        if vegetation < 0.3:
            risk_factors.append("low_vegetation")
        
        return {
            'suitability_score': float(suitability),
            'confidence': 0.6,  # Lower confidence for heuristic
            'risk_factors': risk_factors,
            'model_version': f"{self.version}_heuristic",
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _identify_risk_factors(self, data: Dict, suitability: float) -> List[str]:
        """Identify environmental risk factors."""
        risk_factors = []
        
        temp = data.get('temperature', 25)
        rainfall = data.get('rainfall', 100)
        vegetation = data.get('vegetation_index', 0.5)
        humidity = data.get('humidity', 60)
        
        if temp < 15:
            risk_factors.append("low_temperature")
        elif temp > 35:
            risk_factors.append("high_temperature")
        
        if rainfall < 50:
            risk_factors.append("drought_conditions")
        elif rainfall > 250:
            risk_factors.append("excessive_rainfall")
        
        if vegetation < 0.3:
            risk_factors.append("poor_vegetation")
        
        if humidity > 80:
            risk_factors.append("high_humidity")
        elif humidity < 40:
            risk_factors.append("low_humidity")
        
        if suitability < 0.3:
            risk_factors.append("unsuitable_habitat")
        elif suitability > 0.8:
            risk_factors.append("high_infestation_risk")
        
        return risk_factors
    
    async def train(self, training_data: List[Dict]) -> Dict:
        """
        Train the habitat prediction model.
        
        Args:
            training_data: List of training examples with features and labels
            
        Returns:
            Dict with training metrics
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            
            # Prepare features and labels
            X = df[self.feature_names].fillna(0)
            y = df['suitability_score']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            await self.save_model()
            
            return {
                'training_samples': len(training_data),
                'test_mse': float(mse),
                'test_r2': float(r2),
                'feature_importance': dict(zip(
                    self.feature_names, 
                    self.model.feature_importances_
                )),
                'model_version': self.version,
                'training_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Habitat model training error: {str(e)}")
    
    async def get_status(self) -> Dict:
        """Get model status and information."""
        return {
            'model_loaded': self.model is not None,
            'version': self.version,
            'feature_names': self.feature_names,
            'model_type': 'RandomForestRegressor',
            'last_updated': datetime.now().isoformat()
        }
