from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers_auth import router as auth_router
from .routers_residents import router as residents_router

# Initialize FastAPI app with metadata and tags
app = FastAPI(
    title="Resident Directory API",
    description="REST API for managing residents with authentication, pagination, and search.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Admin authentication endpoints"},
        {"name": "Residents", "description": "Resident directory endpoints"},
        {"name": "Health", "description": "Service health checks"},
    ],
)

# CORS: allow frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables if they do not exist yet (simple approach; migrations optional)
def _create_db():
    Base.metadata.create_all(bind=engine)


_create_db()


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check", description="Simple service health check endpoint.")
def health_check():
    """Returns service health status."""
    return {"message": "Healthy"}


# Include routers
app.include_router(auth_router)
app.include_router(residents_router)
