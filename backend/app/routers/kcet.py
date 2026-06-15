from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.kcet_service import KCETService
from app.services.college_service import KCETCollegeService

router = APIRouter()
kcet_service = KCETService()
college_service = KCETCollegeService()


from typing import Optional

class KCETPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=180, description="Raw marks scored")
    board_marks: Optional[float] = Field(None, ge=0, le=300, description="Board marks out of 300")
    shift: str = Field(default="day1", description="Day")
    category: str = Field(default="general", description="Student category")
    total_candidates: int = Field(default=400000, ge=1)


class PredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int
    board_marks_used: Optional[bool] = None


@router.post("/kcet/", response_model=PredictionResponse)
async def predict_kcet(request: KCETPredictionRequest):
    try:
        result = kcet_service.predict(
            marks=request.marks,
            board_marks=request.board_marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kcet/colleges")
async def get_kcet_colleges(
    rank: int = Query(..., description="Predicted KCET rank"),
    category: str = Query(default="general"),
    limit: int = Query(default=50, le=100),
):
    results = college_service.predict(rank=rank, category=category, limit=limit)
    return {"colleges": results, "total": len(results)}
