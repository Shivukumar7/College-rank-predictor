from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.jee_advanced_service import JEEAdvancedService
from app.services.college_service import JEEAdvancedCollegeService

router = APIRouter()
jee_adv_service = JEEAdvancedService()
college_service = JEEAdvancedCollegeService()


class JEEAdvPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=360, description="Total marks (Paper 1 + Paper 2)")
    shift: str = Field(default="paper1", description="Paper identifier")
    category: str = Field(default="general", description="Student category")
    total_candidates: int = Field(default=180000, ge=1)


from typing import Optional

class PredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int
    eligible: Optional[bool] = None


@router.post("/jee-advanced/", response_model=PredictionResponse)
async def predict_jee_advanced(request: JEEAdvPredictionRequest):
    try:
        result = jee_adv_service.predict(
            marks=request.marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jee-advanced/colleges")
async def get_jee_adv_colleges(
    rank: int = Query(..., description="Predicted JEE Advanced rank"),
    category: str = Query(default="general"),
    limit: int = Query(default=50, le=100),
):
    results = college_service.predict(rank=rank, category=category, limit=limit)
    return {"colleges": results, "total": len(results)}
