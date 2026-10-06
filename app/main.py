from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (registers tables on Base)
from app.database.connection import Base, engine
from app.routes import incidents


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Creates tables if they don't exist. We'll replace this with Alembic migrations later.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Incident Response Platform",
    description="Receives software incidents and manages their lifecycle.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(incidents.router)


@app.get("/health", tags=["system"])
def health_check():
    """Used by humans, load balancers and (later) Docker/AWS to check the API is alive."""
    return {"status": "healthy"}
