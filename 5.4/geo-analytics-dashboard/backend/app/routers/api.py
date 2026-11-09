import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, check_db_connection
from app.schemas.dto import HealthResponse, SummaryMetrics, ObjectOut, ObjectDetailOut, StatusHistoryOut, EventOut, ResourceOut, TimeSeriesPoint, CategoriesAnalyticsResponse, CategoryStatItem

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    info = check_db_connection()
    return HealthResponse(status="ok" if info["connected"] else "degraded", database_connected=info["connected"], postgis_info=info.get("postgis_version", "OK"), objects_in_db=info.get("objects_count", 0), timestamp=datetime.utcnow())

@router.get("/metrics/summary", response_model=SummaryMetrics)
def get_summary_metrics(category: Optional[str] = Query(None), status: Optional[str] = Query(None), severity: Optional[str] = Query(None), db: Session = Depends(get_db)):
    obj_where = "WHERE 1=1"
    params = {}
    if category:
        obj_where += " AND o.category = :category"
        params["category"] = category
    if status:
        obj_where += " AND o.status = :status"
        params["status"] = status
    obj_row = db.execute(text(f"SELECT COUNT(*) AS total_objects, COUNT(*) FILTER (WHERE o.status = 'active') AS active_objects FROM objects o {obj_where}"), params).mappings().first()
    ev_where = f"WHERE e.object_id IN (SELECT o.id FROM objects o {obj_where})"
    if severity:
        ev_where += " AND e.severity = :severity"
        params["severity"] = severity
    ev_row = db.execute(text(f"SELECT COUNT(*) AS total_events, COUNT(*) FILTER (WHERE e.status IN ('open', 'in_progress')) AS open_events FROM events e {ev_where}"), params).mappings().first()
    res_row = db.execute(text(f"SELECT COALESCE(SUM(r.total_amount), 0) AS total_res, COALESCE(SUM(r.available_amount), 0) AS avail_res FROM resources r WHERE r.object_id IN (SELECT o.id FROM objects o {obj_where})"), params).mappings().first()
    total_res = int(res_row["total_res"] or 0)
    avail_res = int(res_row["avail_res"] or 0)
    avail_pct = round((avail_res / total_res * 100.0), 1) if total_res > 0 else 0.0
    return SummaryMetrics(total_objects=int(obj_row["total_objects"] or 0), active_objects=int(obj_row["active_objects"] or 0), total_events=int(ev_row["total_events"] or 0), open_events=int(ev_row["open_events"] or 0), total_resources_units=total_res, available_resources_units=avail_res, resource_availability_pct=avail_pct)

@router.get("/objects", response_model=List[ObjectOut])
def list_objects(category: Optional[str] = Query(None), status: Optional[str] = Query(None), search: Optional[str] = Query(None), db: Session = Depends(get_db)):
    where = "WHERE 1=1"
    params = {}
    if category:
        where += " AND o.category = :category"
        params["category"] = category
    if status:
        where += " AND o.status = :status"
        params["status"] = status
    if search:
        where += " AND (o.name ILIKE :search OR o.code ILIKE :search)"
        params["search"] = f"%{search}%"
    rows = db.execute(text(f"SELECT o.id, o.name, o.object_type, o.category, o.code, o.sidc, o.affiliation, o.echelon, o.status, ST_X(o.geom) AS longitude, ST_Y(o.geom) AS latitude, o.osm_feature_id, osm.name AS osm_feature_name, o.area_id, a.name AS area_name, o.attributes, o.is_synthetic, o.created_at, o.updated_at FROM objects o LEFT JOIN osm_features osm ON osm.osm_id = o.osm_feature_id LEFT JOIN areas a ON a.id = o.area_id {where} ORDER BY o.id ASC"), params).mappings().all()
    return [ObjectOut(**dict(r)) for r in rows]

@router.get("/objects/{object_id}", response_model=ObjectDetailOut)
def get_object_detail(object_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT o.id, o.name, o.object_type, o.category, o.code, o.sidc, o.affiliation, o.echelon, o.status, ST_X(o.geom) AS longitude, ST_Y(o.geom) AS latitude, o.osm_feature_id, osm.name AS osm_feature_name, o.area_id, a.name AS area_name, o.attributes, o.is_synthetic, o.created_at, o.updated_at FROM objects o LEFT JOIN osm_features osm ON osm.osm_id = o.osm_feature_id LEFT JOIN areas a ON a.id = o.area_id WHERE o.id = :object_id"), {"object_id": object_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    hist = db.execute(text("SELECT id, previous_status, new_status, changed_at, reason FROM object_status_history WHERE object_id = :object_id ORDER BY changed_at DESC LIMIT 10"), {"object_id": object_id}).mappings().all()
    data = dict(row)
    data["status_history"] = [StatusHistoryOut(**dict(h)) for h in hist]
    return ObjectDetailOut(**data)

@router.get("/events", response_model=List[EventOut])
def list_events(category: Optional[str] = Query(None), severity: Optional[str] = Query(None), db: Session = Depends(get_db)):
    where = "WHERE 1=1"
    params = {}
    if category:
        where += " AND o.category = :category"
        params["category"] = category
    if severity:
        where += " AND e.severity = :severity"
        params["severity"] = severity
    rows = db.execute(text(f"SELECT e.id, e.title, e.category, e.severity, e.status, e.event_time, ST_X(e.geom) AS longitude, ST_Y(e.geom) AS latitude, e.object_id, o.name AS object_name, o.code AS object_code, e.description, e.is_synthetic FROM events e LEFT JOIN objects o ON o.id = e.object_id {where} ORDER BY e.event_time DESC LIMIT 200"), params).mappings().all()
    return [EventOut(**dict(r)) for r in rows]

@router.get("/resources", response_model=List[ResourceOut])
def list_resources(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT r.id, r.name, r.category, r.total_amount, r.available_amount, r.in_use_amount, r.unit, r.condition, r.object_id, ST_X(r.geom) AS longitude, ST_Y(r.geom) AS latitude, r.is_synthetic, r.updated_at FROM resources r ORDER BY r.id ASC")).mappings().all()
    return [ResourceOut(**dict(r)) for r in rows]

@router.get("/analytics/timeseries", response_model=List[TimeSeriesPoint])
def get_timeseries_analytics(days: int = Query(30), db: Session = Depends(get_db)):
    rows = db.execute(text("WITH ds AS (SELECT generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE, '1 day'::interval)::date AS d), ev AS (SELECT DATE(event_time) AS d, COUNT(*) AS c, COUNT(*) FILTER (WHERE severity IN ('high', 'critical')) AS cr FROM events GROUP BY DATE(event_time)), hs AS (SELECT DATE(changed_at) AS d, COUNT(*) AS ch FROM object_status_history GROUP BY DATE(changed_at)) SELECT TO_CHAR(ds.d, 'YYYY-MM-DD') AS date, COALESCE(ev.c, 0) AS events_count, COALESCE(ev.cr, 0) AS critical_events, COALESCE(hs.ch, 0) AS status_changes, ROUND((84.0 + (EXTRACT(DAY FROM ds.d)::int % 12))::numeric, 1) AS readiness_index FROM ds LEFT JOIN ev ON ev.d = ds.d LEFT JOIN hs ON hs.d = ds.d ORDER BY ds.d ASC")).mappings().all()
    return [TimeSeriesPoint(**dict(r)) for r in rows]

@router.get("/analytics/categories", response_model=CategoriesAnalyticsResponse)
def get_categories_analytics(category: Optional[str] = Query(None), status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    where = "WHERE 1=1"
    params = {}
    if category:
        where += " AND o.category = :category"
        params["category"] = category
    if status:
        where += " AND o.status = :status"
        params["status"] = status
    cat_rows = db.execute(text(f"SELECT o.category AS name, COUNT(*) AS value FROM objects o {where} GROUP BY o.category ORDER BY value DESC"), params).mappings().all()
    stat_rows = db.execute(text(f"SELECT o.status AS name, COUNT(*) AS value FROM objects o {where} GROUP BY o.status ORDER BY value DESC"), params).mappings().all()
    sev_rows = db.execute(text("SELECT severity AS name, COUNT(*) AS value FROM events GROUP BY severity ORDER BY value DESC")).mappings().all()
    res_rows = db.execute(text("SELECT category AS name, COALESCE(SUM(available_amount), 0) AS value, COALESCE(SUM(in_use_amount), 0) AS extra FROM resources GROUP BY category ORDER BY value DESC")).mappings().all()
    return CategoriesAnalyticsResponse(by_category=[CategoryStatItem(name=r["name"], value=int(r["value"])) for r in cat_rows], by_status=[CategoryStatItem(name=r["name"], value=int(r["value"])) for r in stat_rows], by_severity=[CategoryStatItem(name=r["name"], value=int(r["value"])) for r in sev_rows], resources_comparison=[CategoryStatItem(name=r["name"], value=int(r["value"]), extra=int(r["extra"])) for r in res_rows])

@router.get("/map/geojson")
def get_map_geojson(db: Session = Depends(get_db)):
    area_rows = db.execute(text("SELECT id, name, area_type, area_sq_km, attributes, ST_AsGeoJSON(geom) AS geom_json FROM areas")).mappings().all()
    features = [{"type": "Feature", "id": f"area-{a['id']}", "geometry": json.loads(a["geom_json"]), "properties": {"layer": "areas", "id": a["id"], "name": a["name"], "area_type": a["area_type"], "area_sq_km": float(a["area_sq_km"])}} for a in area_rows]
    return {"type": "FeatureCollection", "features": features}

@router.get("/osm/features")
def get_osm_features(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT osm_id, osm_type, name, category, tags, is_synthetic, ST_AsGeoJSON(geom) AS geom_json FROM osm_features ORDER BY osm_id ASC")).mappings().all()
    features = [{"type": "Feature", "id": f"osm-{r['osm_id']}", "geometry": json.loads(r["geom_json"]), "properties": {"osm_id": r["osm_id"], "name": r["name"], "category": r["category"]}} for r in rows]
    return {"type": "FeatureCollection", "features": features}