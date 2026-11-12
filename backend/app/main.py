from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routes.analyst import router as analyst_router
from app.routes.audit import router as audit_router
from app.routes.auth import router as auth_router
from app.routes.customers import router as customers_router
from app.routes.documents import router as documents_router
from app.routes.risk import router as risk_router
from app.routes.verification import router as verification_router

if os.getenv("APP_ENV") == "production":
    if len(settings.secret_key) < 32 or "replace-me" in settings.secret_key:
        raise RuntimeError("Set a strong SECRET_KEY of at least 32 characters for production.")
    if not settings.gcs_bucket_name or not settings.google_cloud_project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT and GCS_BUCKET_NAME must be configured for production document storage.")

if os.getenv("APP_ENV") != "production":
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Northgate eKYC backend for customer onboarding, document review, verification, "
        "risk assessment, and analyst decisions."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(customers_router, prefix=f"{settings.api_v1_prefix}/customers", tags=["Customers"])
app.include_router(documents_router, prefix=f"{settings.api_v1_prefix}/documents", tags=["Documents"])
app.include_router(verification_router, prefix=f"{settings.api_v1_prefix}/verification", tags=["Verification"])
app.include_router(risk_router, prefix=f"{settings.api_v1_prefix}/risk", tags=["Risk"])
app.include_router(analyst_router, prefix=f"{settings.api_v1_prefix}/analyst", tags=["Analyst"])
app.include_router(audit_router, prefix=f"{settings.api_v1_prefix}/audit", tags=["Audit"])


@app.get("/")
def home_page() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def readiness() -> dict[str, str]:
    return {"service": settings.app_name, "status": "healthy"}


@app.get("/ui")
def ui_page() -> FileResponse:
    return FileResponse(static_dir / "index.html")
