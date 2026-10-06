import logging

from fastapi import FastAPI

from app.errors import register_exception_handlers
from app.routes import auth, incidents

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


app = FastAPI(
    title="Incident Response Platform",
    description="Receives software incidents and manages their lifecycle.",
    version="0.1.0",
)

register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(incidents.router)


@app.get("/health", tags=["system"])
def health_check():
    """Used by humans, load balancers and (later) Docker/AWS to check the API is alive."""
    return {"status": "healthy"}
