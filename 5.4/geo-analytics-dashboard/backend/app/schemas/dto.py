from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    postgis_info: str
    objects_in_db: int
    timestamp: datetime

class SummaryMetrics(BaseModel):
    total_objects: int
    active_objects: int
    total_events: int
    open_events: int
    total_resources_units: int
    available_resources_units: int
    resource_availability_pct: float

class ObjectOut(BaseModel):
    id: int
    name: str
    object_type: str
    category: str
    code: str
    sidc: str
    affiliation: str
    echelon: str
    status: str
    longitude: float
    latitude: float
    osm_feature_id: Optional[int] = None
    osm_feature_name: Optional[str] = None
    area_id: Optional[int] = None
    area_name: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    is_synthetic: bool = True
    created_at: datetime
    updated_at: datetime

class StatusHistoryOut(BaseModel):
    id: int
    previous_status: str
    new_status: str
    changed_at: datetime
    reason: str

class ObjectDetailOut(ObjectOut):
    status_history: List[StatusHistoryOut] = Field(default_factory=list)
    recent_events_count: int = 0
    assigned_resources_count: int = 0

class EventOut(BaseModel):
    id: int
    title: str
    category: str
    severity: str
    status: str
    event_time: datetime
    longitude: float
    latitude: float
    object_id: Optional[int] = None
    object_name: Optional[str] = None
    object_code: Optional[str] = None
    description: str
    is_synthetic: bool = True

class ResourceOut(BaseModel):
    id: int
    name: str
    category: str
    total_amount: int
    available_amount: int
    in_use_amount: int
    unit: str
    condition: str
    object_id: Optional[int] = None
    longitude: float
    latitude: float
    is_synthetic: bool = True
    updated_at: datetime

class TimeSeriesPoint(BaseModel):
    date: str
    events_count: int
    critical_events: int
    status_changes: int
    readiness_index: float

class CategoryStatItem(BaseModel):
    name: str
    value: int
    extra: Optional[int] = 0

class CategoriesAnalyticsResponse(BaseModel):
    by_category: List[CategoryStatItem]
    by_status: List[CategoryStatItem]
    by_severity: List[CategoryStatItem]
    resources_comparison: List[CategoryStatItem]
