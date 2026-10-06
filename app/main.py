from fastapi import FastAPI

app = FastAPI(
    title="Incident Response Platform",
    description="Receives software incidents and manages their lifecycle.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check():
    """Used by humans, load balancers and (later) Docker/AWS to check the API is alive."""
    return {"status": "healthy"}
