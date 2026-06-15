from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import jee_main, jee_advanced, neet, kcet, mht_cet, comedk, health, counseling

app = FastAPI(
    title=settings.APP_NAME,
    description="ML-powered rank prediction for Indian competitive exams",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes — NO prefix here, prefixes are in routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(jee_main.router, prefix="/predict", tags=["JEE Main"])
app.include_router(jee_advanced.router, prefix="/predict", tags=["JEE Advanced"])
app.include_router(neet.router, prefix="/predict", tags=["NEET"])
app.include_router(kcet.router, prefix="/predict", tags=["KCET"])
app.include_router(mht_cet.router, prefix="/predict", tags=["MHT-CET"])
app.include_router(comedk.router, prefix="/predict", tags=["COMEDK"])
app.include_router(counseling.router, prefix="/predict", tags=["Counseling"])

@app.get("/")
async def root():
    return {
        "message": "ExamRank AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "exams_supported": ["jee-main", "jee-advanced", "neet", "kcet", "mht-cet", "comedk"]
    }
