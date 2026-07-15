from fastapi import FastAPI

from src.api.routes import health, webhooks
from src.logging import setup_logging

# Setup logging first — before anything else
setup_logging()

app = FastAPI(
    title="Srijan",
    description="AI-powered engineering assistant for chat platforms",
    version="0.1.0",
)

# Register route handlers
app.include_router(health.router, tags=["Health"])
app.include_router(webhooks.router, tags=["Webhooks"])