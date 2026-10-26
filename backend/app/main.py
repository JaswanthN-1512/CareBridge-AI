"""Main FastAPI application entry point for CareBridge AI."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from app.config import get_settings
from app.models.response_models import HealthResponse, ErrorResponse

# Configure structured logging
settings = get_settings()
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("carebridge.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown routines."""
    logger.info("Starting CareBridge AI backend service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Embeddings: {settings.EMBEDDING_PROVIDER}")
    logger.info(f"Vector Store: {settings.VECTOR_STORE_TYPE}")
    logger.info(f"CORS Allowed Origins: {settings.cors_origins}")
    yield
    logger.info("Shutting down CareBridge AI backend service...")


app = FastAPI(
    title="CareBridge AI API",
    description="AI-Powered Healthcare Navigation & Document Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject industry-standard security headers onto every outbound HTTP response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request payload validation errors with structured JSON envelope."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=True,
            code="VALIDATION_ERROR",
            message="The submitted request contained invalid or missing fields.",
            details={"errors": jsonable_encoder(exc.errors())},
        ).model_dump(),
    )


from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(HTTPException)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle deliberate HTTP exceptions with structured JSON envelope."""
    logger.warning(f"HTTP exception on {request.url.path}: status={exc.status_code}, detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=True,
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler to prevent leaking internal traces."""
    logger.exception(f"Unhandled error processing request to {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=True,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected system error occurred. Please try again or contact support.",
        ).model_dump(),
    )


# Base Routes
@app.get("/", tags=["General"])
async def root():
    """Root endpoint providing service identification and API documentation link."""
    return {
        "service": "CareBridge AI API",
        "title": "AI-Powered Healthcare Navigation & Document Intelligence Platform",
        "tagline": "Understand your healthcare documents. Prepare better conversations.",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    include_in_schema=False,
)
@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="System Health & Diagnostic Telemetry",
)
async def health_check():
    """Verify backend operational status, active LLM provider, and vector store configuration."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        llm_provider=settings.LLM_PROVIDER,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        vector_store_type=settings.VECTOR_STORE_TYPE,
    )


# Mount Core API Routers
from app.api.routes_upload import router as upload_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_chat import router as chat_router
from app.api.routes_samples import router as samples_router

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(samples_router)

