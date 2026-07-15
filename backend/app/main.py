import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import auth_router, predict_router, report_router, assessment_router
from ml.model import load_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load ML model and create DB tables. Shutdown: cleanup."""
    logger.info("Loading ML model...")
    load_model()
    logger.info("ML model loaded")

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    yield


app = FastAPI(
    title="HeartGuard API",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_origin_regex="https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(predict_router.router, prefix="/api", tags=["Prediction"])
app.include_router(report_router.router, prefix="/api", tags=["Reports"])
app.include_router(assessment_router.router, prefix="/api", tags=["Assessments"])


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict:
    """Application health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
