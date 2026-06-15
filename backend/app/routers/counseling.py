from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.counseling_service import CounselingService
from app.services.college_service import (
    JEEMainCollegeService,
    JEEAdvancedCollegeService,
    NEETCollegeService,
    KCETCollegeService,
    MHTCETCollegeService,
    COMEDKCollegeService,
    get_roi_ranked_list,
    get_placement_info,
)


router = APIRouter()
counseling_service = CounselingService()

# Instantiate college services for trends
jee_main_college = JEEMainCollegeService()
jee_advanced_college = JEEAdvancedCollegeService()
neet_college = NEETCollegeService()
kcet_college = KCETCollegeService()
mht_cet_college = MHTCETCollegeService()
comedk_college = COMEDKCollegeService()


import time
from fastapi import Request

# In-memory sliding window rate limiting
RATE_LIMIT_LIMIT = 10  # max requests
RATE_LIMIT_WINDOW = 60  # seconds (1 minute)
client_requests: Dict[str, List[float]] = {}

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    if ip not in client_requests:
        client_requests[ip] = []
    # Filter timestamps older than the rate limit window
    client_requests[ip] = [t for t in client_requests[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(client_requests[ip]) >= RATE_LIMIT_LIMIT:
        return True
    client_requests[ip].append(now)
    return False

class OptimizeRequest(BaseModel):
    colleges: List[Dict]
    branch_preferences: Optional[List[str]] = None


class ChatContext(BaseModel):
    exam: Optional[str] = None
    rank: Optional[int] = None
    category: Optional[str] = None
    preferred_branches: Optional[List[str]] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None


@router.post("/optimize-choices/")
async def optimize_choices(request: OptimizeRequest):
    try:
        optimized = counseling_service.optimize_choices(request.colleges, request.branch_preferences)
        return {"colleges": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chatbot/")
async def chatbot_reply(chat_req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute before sending another message."
        )
    try:
        context_dict = chat_req.context.dict() if chat_req.context else None
        reply = counseling_service.chat_response(chat_req.message, context_dict)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/")
async def get_trends(
    exam: str = Query(..., description="Exam name (e.g., jee-main, jee-advanced, neet, kcet)"),
    institute: str = Query(..., description="College or Institute name"),
    branch: str = Query(..., description="Branch or Course name"),
    category: str = Query(default="general"),
    quota: str = Query(default="Other State"),
):
    try:
        exam_clean = exam.lower().strip()
        if exam_clean == "jee-main":
            trends = jee_main_college.get_cutoff_trends(institute, branch, category, quota)
        elif exam_clean == "jee-advanced":
            trends = jee_advanced_college.get_cutoff_trends(institute, branch, category, quota)
        elif exam_clean == "neet":
            trends = neet_college.get_cutoff_trends(institute, branch, category, quota)
        elif exam_clean == "kcet":
            trends = kcet_college.get_cutoff_trends(institute, branch, category, quota)
        elif exam_clean == "mht-cet":
            trends = mht_cet_college.get_cutoff_trends(institute, branch, category, quota)
        elif exam_clean == "comedk":
            trends = comedk_college.get_cutoff_trends(institute, branch, category, quota)
        else:
            raise HTTPException(status_code=400, detail="Invalid exam type")
            
        return {"trends": trends, "institute": institute, "branch": branch}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RoiRequest(BaseModel):
    colleges: List[Dict]


@router.post("/roi-ranking/")
async def get_roi_ranking(request: RoiRequest):
    """
    Accepts a list of college dicts and returns them enriched with placement/ROI data,
    sorted by ROI index (avg package / total fees) descending.
    """
    try:
        ranked = get_roi_ranked_list(request.colleges)
        return {"colleges": ranked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/placement-info/")
async def placement_info(college_name: str = Query(..., description="College name to look up")):
    """Return placement, fees, and ROI data for a specific college."""
    try:
        info = get_placement_info(college_name)
        if not info:
            return {"found": False, "college": college_name}
        return {"found": True, "college": college_name, **info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
