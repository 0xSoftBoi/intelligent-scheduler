"""Energy analysis API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.energy_analysis.energy_analyzer import EnergyAnalyzer
from src.core.security import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])
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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
