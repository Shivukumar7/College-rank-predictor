from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.jee_main_service import JEEMainService
from app.services.college_service import JEEMainCollegeService

router = APIRouter()
jee_service = JEEMainService()
college_service = JEEMainCollegeService()

class JEEPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=300, description="Raw marks scored")
    shift: str = Field(..., description="Exam shift (e.g., 'shift1', 'shift2')")
    category: str = Field(..., description="Student category")
    total_candidates: int = Field(default=1200000, ge=1)

class JEEPredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int

@router.post("/jee-main/", response_model=JEEPredictionResponse)
async def predict_jee_main(request: JEEPredictionRequest):
    try:
        result = jee_service.predict(
            marks=request.marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jee-main/shift-stats/{shift}")
async def get_shift_stats(shift: str):
    if shift not in jee_service.shift_stats:
        raise HTTPException(status_code=404, detail=f"Shift '{shift}' not found")
    return jee_service.shift_stats[shift]

@router.get("/jee-main/global-stats")
async def get_global_stats():
    return jee_service.global_stats

@router.get("/jee-main/colleges")
async def get_jee_main_colleges(
    rank: int = Query(..., description="Predicted JEE Main rank"),
    category: str = Query(default="general"),
    quota: str = Query(default="Other State", description="Seat quota (Home State or Other State)"),
    limit: int = Query(default=50, le=100),
):
    results = college_service.predict(rank=rank, category=category, quota=quota, limit=limit)
    return {"colleges": results, "total": len(results)}

