"""Energy analysis API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.energy_analysis.energy_analyzer import EnergyAnalyzer

router = APIRouter()
analyzer = EnergyAnalyzer()


class EnergyPatternRequest(BaseModel):
    user_id: str
    days: int = 30


class EnergyPredictionRequest(BaseModel):
    user_id: str
    target_datetime: datetime


@router.get("/patterns")
async def get_energy_patterns(user_id: str, days: int = 30):
    """Get energy patterns for a user."""
    try:
        patterns = analyzer.analyze_historical_patterns(user_id, days)
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_energy(request: EnergyPredictionRequest):
    """Predict energy level for a specific time."""
    try:
        energy_level = analyzer.predict_energy_level(
            request.user_id,
            request.target_datetime
        )
        
        return {
            "user_id": request.user_id,
            "target_datetime": request.target_datetime,
            "predicted_energy_level": energy_level,
            "confidence": 0.85
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
