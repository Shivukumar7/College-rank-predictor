from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.neet_service import NEETService
from app.services.college_service import NEETCollegeService

router = APIRouter()
neet_service = NEETService()
college_service = NEETCollegeService()


class NEETPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=720, description="Raw marks scored")
    shift: str = Field(default="single", description="Session")
    category: str = Field(default="general", description="Student category")
    total_candidates: int = Field(default=2400000, ge=1)


class PredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int


@router.post("/neet/", response_model=PredictionResponse)
async def predict_neet(request: NEETPredictionRequest):
    try:
        result = neet_service.predict(
            marks=request.marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/neet/colleges")
async def get_neet_colleges(
    rank: int = Query(default=None),
    marks: int = Query(default=None),
    category: str = Query(default="general"),
    limit: int = Query(default=50, le=100),
):
    if marks is None and rank is None:
        raise HTTPException(status_code=400, detail="Provide either 'marks' or 'rank'")
    # NEET uses marks-based cutoffs
    effective_marks = marks if marks is not None else max(0, 720 - int(rank * 720 / 2400000))
    results = college_service.predict(marks=effective_marks, category=category, limit=limit)
    return {"colleges": results, "total": len(results)}
