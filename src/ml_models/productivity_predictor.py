"""Machine learning model for productivity prediction."""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from sklearn.ensemble import XGBRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
from loguru import logger


class ProductivityPredictor:
    """ML model for predicting user productivity and task completion."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = [
            'hour', 'day_of_week', 'energy_level', 'task_type',
            'task_priority', 'time_blocked_minutes', 'meetings_before',
            'context_switches', 'focus_time_available'
        ]
        
        if model_path:
            self.load_model(model_path)

    def train(self, training_data: pd.DataFrame) -> Dict:
        """Train productivity prediction model.
        
        Args:
            training_data: Historical productivity data
            
        Returns:
            Training metrics
        """
        logger.info(f"Training productivity predictor with {len(training_data)} samples")
        
        # Prepare features and target
        X = self._prepare_features(training_data)
        y = training_data['productivity_score']  # 0-100 score
        
        # Train XGBoost model
        self.model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        self.model.fit(X, y)
        
        # Calculate metrics
        train_score = self.model.score(X, y)
        predictions = self.model.predict(X)
        mae = np.mean(np.abs(predictions - y))
        
        metrics = {
            'r2_score': train_score,
            'mae': mae,
            'train_samples': len(X)
        }
        
        logger.info(f"Training complete. R²: {train_score:.3f}, MAE: {mae:.3f}")
        
        return metrics

    def predict_productivity(self, time_slot: datetime, task_type: str,
                           context: Dict) -> float:
        """Predict productivity for a task at a specific time.
        
        Args:
            time_slot: Scheduled time
            task_type: Type of task
            context: Additional context information
            
        Returns:
            Predicted productivity score (0-100)
        """
        if not self.model:
            raise ValueError("Model not trained or loaded")
        
        # Create feature DataFrame
        features = pd.DataFrame([{
            'hour': time_slot.hour,
            'day_of_week': time_slot.weekday(),
            'energy_level': context.get('energy_level', 70),
            'task_type': task_type,
            'task_priority': context.get('priority', 5),
            'time_blocked_minutes': context.get('duration_minutes', 60),
            'meetings_before': context.get('meetings_before', 0),
            'context_switches': context.get('context_switches', 0),
            'focus_time_available': context.get('focus_time_available', 120)
        }])
        
        X = self._prepare_features(features)
        prediction = self.model.predict(X)
        
        return float(np.clip(prediction[0], 0, 100))

    def recommend_task_timing(self, tasks: List[Dict], 
                            time_slots: List[datetime],
                            user_context: Dict) -> List[Dict]:
        """Recommend optimal timing for tasks.
        
        Args:
            tasks: List of tasks to schedule
            time_slots: Available time slots
            user_context: User context information
            
        Returns:
            List of task-slot recommendations with scores
        """
        recommendations = []
        
        for task in tasks:
            best_slot = None
            best_score = -1
            
            for slot in time_slots:
                context = {
                    **user_context,
                    'priority': task.get('priority', 5),
                    'duration_minutes': task.get('duration_minutes', 60)
                }
                
                score = self.predict_productivity(
                    slot, task['type'], context
                )
                
                if score > best_score:
                    best_score = score
                    best_slot = slot
            
            recommendations.append({
                'task_id': task['id'],
                'task_title': task['title'],
                'recommended_slot': best_slot,
                'productivity_score': best_score,
                'task_type': task['type']
            })
        
        # Sort by productivity score
        recommendations.sort(key=lambda x: x['productivity_score'], reverse=True)
        
        return recommendations

    def save_model(self, path: str):
        """Save model to disk."""
        if not self.model:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from disk."""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        
        logger.info(f"Model loaded from {path}")

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from raw data."""
        features = data.copy()
        
        # Encode categorical features
        categorical_cols = ['task_type']
        
        for col in categorical_cols:
            if col in features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    features[col] = self.label_encoders[col].fit_transform(
                        features[col].astype(str)
                    )
                else:
                    # Handle unseen categories
                    features[col] = features[col].apply(
                        lambda x: self._encode_with_unknown(col, x)
                    )
        
        # Fill missing features
        for col in self.feature_columns:
            if col not in features.columns:
                features[col] = 0
        
        return features[self.feature_columns]

    def _encode_with_unknown(self, column: str, value: str) -> int:
        """Encode value, handling unknown categories."""
        encoder = self.label_encoders[column]
        try:
            return encoder.transform([str(value)])[0]
        except ValueError:
            # Unknown category, return default
            return 0
