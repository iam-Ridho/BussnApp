from fastapi import FastAPI

from app.api import health

app = FastAPI(title="BussnApp API", version="0.1.0", docs_url="/docs")
app.include_router(health.router, prefix="/api/v1")
