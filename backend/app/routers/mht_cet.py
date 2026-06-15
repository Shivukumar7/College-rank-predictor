from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.mht_cet_service import MHTCETService
from app.services.college_service import MHTCETCollegeService

router = APIRouter()
mht_cet_service = MHTCETService()
college_service = MHTCETCollegeService()


class MHTCETPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=200, description="Raw marks scored")
    shift: str = Field(default="pcm", description="Group (PCM/PCB)")
    category: str = Field(default="general", description="Student category")
    total_candidates: int = Field(default=450000, ge=1)


class PredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int


@router.post("/mht-cet/", response_model=PredictionResponse)
async def predict_mht_cet(request: MHTCETPredictionRequest):
    try:
        result = mht_cet_service.predict(
            marks=request.marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mht-cet/colleges")
async def get_mht_cet_colleges(
    rank: int = Query(..., description="Predicted MHT-CET rank"),
    category: str = Query(default="general"),
    limit: int = Query(default=50, le=100),
):
    results = college_service.predict(rank=rank, category=category, limit=limit)
    return {"colleges": results, "total": len(results)}
