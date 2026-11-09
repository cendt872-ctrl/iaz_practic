import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api.router, prefix=settings.API_V1_STR, tags=["GeoAnalytics API"])

@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "version": settings.VERSION, "docs": "/docs"}
