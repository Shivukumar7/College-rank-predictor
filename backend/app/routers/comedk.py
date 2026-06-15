from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.comedk_service import COMEDKService
from app.services.college_service import COMEDKCollegeService

router = APIRouter()
comedk_service = COMEDKService()
college_service = COMEDKCollegeService()


class COMEDKPredictionRequest(BaseModel):
    marks: float = Field(..., ge=0, le=180, description="Raw marks scored")
    shift: str = Field(default="single", description="Session")
    category: str = Field(default="general", description="Student category")
    total_candidates: int = Field(default=90000, ge=1)


class PredictionResponse(BaseModel):
    predicted_rank: int
    category_rank: int
    percentile: float
    normalized_marks: float
    confidence: float
    shift: str
    category: str
    total_candidates: int


@router.post("/comedk/", response_model=PredictionResponse)
async def predict_comedk(request: COMEDKPredictionRequest):
    try:
        result = comedk_service.predict(
            marks=request.marks,
            shift=request.shift,
            category=request.category,
            total_candidates=request.total_candidates,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comedk/colleges")
async def get_comedk_colleges(
    rank: int = Query(..., description="Predicted COMEDK rank"),
    category: str = Query(default="general"),
    limit: int = Query(default=50, le=100),
):
    results = college_service.predict(rank=rank, category=category, limit=limit)
    return {"colleges": results, "total": len(results)}
