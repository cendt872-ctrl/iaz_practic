import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> dict:
    try:
        with engine.connect() as conn:
            postgis_ver = conn.execute(text("SELECT PostGIS_Full_Version();")).scalar()
            obj_count = conn.execute(text("SELECT COUNT(*) FROM objects;")).scalar()
            return {"connected": True, "postgis_version": str(postgis_ver)[:80] if postgis_ver else "Available", "objects_count": obj_count}
    except Exception as exc:
        logger.error("DB connection error: %s", exc)
        return {"connected": False, "error": str(exc), "objects_count": 0}
