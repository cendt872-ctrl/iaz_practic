from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base

class OsmFeature(Base):
    __tablename__ = "osm_features"
    osm_id = Column(BigInteger, primary_key=True, index=True)
    osm_type = Column(String(32), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    geom = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)
    tags = Column(JSONB, nullable=False, default=dict)
    is_synthetic = Column(Boolean, nullable=False, default=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
