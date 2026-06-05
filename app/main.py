from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401


settings = get_settings()


def create_app() -> FastAPI:
    # This function builds and returns the FastAPI application.
    # Keeping setup inside a function makes the app easier to test later.

    # Importing models above registers tables on Base.metadata.
    # create_all is fine for a small demo app; production apps usually use Alembic.
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        # These values appear in /docs and /redoc.
        title=settings.app_name,
        version="1.0.0",
    )

    # CORS allows a browser-based React frontend to call this backend.
    # Without CORS, the browser can block frontend requests even if the API works.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,

        # Allows cookies/auth headers if you add login later.
        allow_credentials=True,

        # Accept all HTTP methods: GET, POST, PUT, PATCH, DELETE, etc.
        allow_methods=["*"],

        # Accept common request headers such as Content-Type and Authorization.
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        # Lightweight endpoint for checking that the API process is alive.
        return {"status": "ok", "environment": settings.app_env}

    # Adds all /api/v1 routes from app/api.py.
    # Example final route: /api/v1/users
    app.include_router(api_router)
    return app


# Uvicorn looks for this object when running: python -m uvicorn app.main:app
app = create_app()
