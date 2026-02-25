"""Machine learning model for energy level prediction."""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
import joblib
from loguru import logger


class EnergyPredictor:
    """ML model for predicting user energy levels."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_morning', 'is_afternoon', 'is_evening',
            'hours_since_sleep', 'meetings_today', 'energy_yesterday'
        ]
        
        if model_path:
            self.load_model(model_path)

    def train(self, training_data: pd.DataFrame, target_col: str = 'energy_level') -> Dict:
        """Train the energy prediction model.
        
        Args:
            training_data: DataFrame with historical energy data
            target_col: Name of target column
            
        Returns:
            Training metrics
        """
        logger.info(f"Training energy predictor with {len(training_data)} samples")
        
        # Prepare features
        X = self._prepare_features(training_data)
        y = training_data[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble model
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        # Train both models
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Ensemble prediction (average)
        self.model = {'rf': rf_model, 'gb': gb_model}
        
        # Evaluate
        rf_score = rf_model.score(X_test_scaled, y_test)
        gb_score = gb_model.score(X_test_scaled, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
        
        metrics = {
            'rf_r2_score': rf_score,
            'gb_r2_score': gb_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        logger.info(f"Training complete. RF R²: {rf_score:.3f}, GB R²: {gb_score:.3f}")
        
        return metrics

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Predict energy levels.
        
        Args:
            features: DataFrame with feature data
            
        Returns:
            Predicted energy levels
        """
        if not self.model:
            raise ValueError("Model not trained or loaded")
        
        X = self._prepare_features(features)
        X_scaled = self.scaler.transform(X)
        
        # Ensemble prediction
        rf_pred = self.model['rf'].predict(X_scaled)
        gb_pred = self.model['gb'].predict(X_scaled)
        
        # Average predictions
        predictions = (rf_pred + gb_pred) / 2
        
        # Clip to valid range
        return np.clip(predictions, 0, 100)

    def predict_single(self, timestamp: datetime, context: Dict) -> float:
        """Predict energy level for a single time point.
        
        Args:
            timestamp: Time to predict for
            context: Additional context (meetings, sleep, etc.)
            
        Returns:
            Predicted energy level
        """
        # Create feature DataFrame
        features = pd.DataFrame([{
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day,
            'month': timestamp.month,
            'is_weekend': timestamp.weekday() >= 5,
            'hours_since_sleep': context.get('hours_since_sleep', 8),
            'meetings_today': context.get('meetings_today', 0),
            'energy_yesterday': context.get('energy_yesterday', 70)
        }])
        
        prediction = self.predict(features)
        return float(prediction[0])

    def save_model(self, path: str):
        """Save trained model to disk.
        
        Args:
            path: File path to save model
        """
        if not self.model:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load trained model from disk.
        
        Args:
            path: File path to load model from
        """
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        
        logger.info(f"Model loaded from {path}")

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.model:
            raise ValueError("Model not trained")
        
        # Get importance from Random Forest
        importances = self.model['rf'].feature_importances_
        
        return dict(zip(self.feature_columns, importances))

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from raw data.
        
        Args:
            data: Raw data DataFrame
            
        Returns:
            Feature DataFrame
        """
        features = data.copy()
        
        # Create time-based features if not present
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features['day_of_month'] = pd.to_datetime(features['timestamp']).dt.day
            features['month'] = pd.to_datetime(features['timestamp']).dt.month
        
        # Create derived features
        if 'hour' in features.columns:
            features['is_morning'] = (features['hour'] >= 6) & (features['hour'] < 12)
            features['is_afternoon'] = (features['hour'] >= 12) & (features['hour'] < 18)
            features['is_evening'] = (features['hour'] >= 18) & (features['hour'] < 24)
        
        if 'day_of_week' in features.columns:
            features['is_weekend'] = features['day_of_week'] >= 5
        
        # Fill missing values with defaults
        for col in self.feature_columns:
            if col not in features.columns:
                features[col] = 0
        
        # Select and order features
        return features[self.feature_columns]
