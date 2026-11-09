import json
import math
import sqlite3
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from threading import Timer
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "local_geo_analytics.db"

app = FastAPI(
    title="ІАС Геопросторового Моніторингу ЗСУ (Демо)",
    version="1.0.0",
    description="Локальний сервер FastAPI + SQL-база + Web-Dashboard (milsymbol + Leaflet + Брендбук ЗСУ)",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS object_status_history;
    DROP TABLE IF EXISTS events;
    DROP TABLE IF EXISTS resources;
    DROP TABLE IF EXISTS objects;
    DROP TABLE IF EXISTS areas;
    DROP TABLE IF EXISTS osm_features;

    CREATE TABLE osm_features (
        osm_id INTEGER PRIMARY KEY,
        osm_type TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        lon REAL NOT NULL,
        lat REAL NOT NULL,
        tags TEXT NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 0,
        fetched_at TEXT NOT NULL
    );

    CREATE TABLE areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        area_type TEXT NOT NULL,
        coords_json TEXT NOT NULL,
        area_sq_km REAL NOT NULL,
        attributes TEXT NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        object_type TEXT NOT NULL,
        category TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        sidc TEXT NOT NULL,
        affiliation TEXT NOT NULL,
        echelon TEXT NOT NULL,
        status TEXT NOT NULL,
        lon REAL NOT NULL,
        lat REAL NOT NULL,
        osm_feature_id INTEGER,
        area_id INTEGER,
        attributes TEXT NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        status TEXT NOT NULL,
        event_time TEXT NOT NULL,
        lon REAL NOT NULL,
        lat REAL NOT NULL,
        object_id INTEGER,
        description TEXT NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        total_amount INTEGER NOT NULL,
        available_amount INTEGER NOT NULL,
        in_use_amount INTEGER NOT NULL,
        unit TEXT NOT NULL,
        condition TEXT NOT NULL,
        object_id INTEGER,
        lon REAL NOT NULL,
        lat REAL NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 1,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE object_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_id INTEGER NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        changed_at TEXT NOT NULL,
        reason TEXT NOT NULL,
        is_synthetic INTEGER NOT NULL DEFAULT 1
    );
    """)

    now = datetime.utcnow()
    osm_Init = [
        (26150422, "node", "Кропивницький", "city", 32.2623, 48.5079),
        (25870505, "node", "Черкаси", "city", 32.0588, 49.4444),
        (26150198, "node", "Вінниця", "city", 28.4682, 49.2331),
        (26150301, "node", "Полтава", "city", 34.5514, 49.5883),
        (31490011, "node", "Умань", "town", 30.2218, 48.7484),
        (31490012, "node", "Олександрія", "town", 33.1169, 48.6696),
        (31490016, "node", "Біла Церква", "city", 30.1121, 49.7956),
        (31490017, "node", "Кременчук", "city", 33.4100, 49.0685),
        (31490018, "node", "Житомир", "city", 28.6587, 50.2547),
    ]
    for oid, otype, name, cat, lon, lat in osm_Init:
        cur.execute(
            "INSERT INTO osm_features VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
            (oid, otype, name, cat, lon, lat, json.dumps({"place": cat}), now.isoformat()),
        )

    areas_init = [
        (
            "Сектор моніторингу «Центр-Північ»",
            "monitoring_zone",
            [[[29.50, 49.90], [32.20, 49.90], [32.20, 48.80], [29.50, 48.80], [29.50, 49.90]]],
            24180.5,
            {"code": "SEC-CN-01"},
        ),
        (
            "Сектор логістичного забезпечення «Інгул»",
            "logistics_sector",
            [[[31.20, 48.80], [33.60, 48.80], [33.60, 47.80], [31.20, 47.80], [31.20, 48.80]]],
            19850.0,
            {"code": "LOG-IN-02"},
        ),
        (
            "Навчально-тренувальний полігон «Поділля-Синтетик»",
            "training_polygon",
            [[[27.80, 49.60], [29.50, 49.60], [29.50, 48.50], [27.80, 48.50], [27.80, 49.60]]],
            15420.0,
            {"code": "TRN-PD-03"},
        ),
        (
            "Район радіотехнічного контролю «Схід-Дніпро»",
            "communications_sector",
            [[[33.40, 50.10], [35.40, 50.10], [35.40, 48.80], [33.40, 48.80], [33.40, 50.10]]],
            21300.0,
            {"code": "COM-DN-04"},
        ),
    ]
    for name, atype, coords, sqkm, attrs in areas_init:
        cur.execute(
            "INSERT INTO areas (name, area_type, coords_json, area_sq_km, attributes, is_synthetic) VALUES (?, ?, ?, ?, ?, 1)",
            (name, atype, json.dumps(coords), sqkm, json.dumps(attrs)),
        )

    types_arr = ["command_post", "mechanized_unit", "air_defense", "logistics_hub", "comms_node", "radar_station"]
    cats_arr = [
        "Сухопутні війська",
        "Повітряні Сили",
        "Військово-Морські Сили",
        "Десантно-штурмові війська",
        "Сили спеціальних операцій",
        "Сили територіальної оборони",
        "Морська піхота",
        "Військова служба правопорядку",
    ]
    sidc_arr = [
        "SFGPE-----F----",
        "SFGPUCI---F----",
        "SFGPUCD---F----",
        "SFGPUSS---F----",
        "SFGPUSM---F----",
        "SFGPUCF---F----",
    ]
    status_arr = ["active", "active", "active", "standby", "maintenance", "relocating"]
    echelon_arr = ["platoon", "company", "battalion", "brigade"]

    for i in range(1, 81):
        v_type = types_arr[i % len(types_arr)]
        v_cat = cats_arr[i % len(cats_arr)]
        v_sidc = sidc_arr[i % len(sidc_arr)]
        v_status = status_arr[(i * 3) % len(status_arr)]
        v_echelon = echelon_arr[i % len(echelon_arr)]
        v_lon = round(28.15 + ((i * 37) % 690) / 100.0 + math.sin(i) * 0.12, 5)
        v_lat = round(47.75 + ((i * 53) % 255) / 100.0 + math.cos(i) * 0.09, 5)
        v_osm_id = osm_Init[i % len(osm_Init)][0]
        v_area_id = 1 + (i % 4)
        created = (now - timedelta(days=40 - (i % 35))).isoformat()

        cur.execute(
            """INSERT INTO objects (
                name, object_type, category, code, sidc, affiliation, echelon, status,
                lon, lat, osm_feature_id, area_id, attributes, is_synthetic, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'friendly', ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (
                f"Умовний об'єкт #{i:03d} ({v_cat})",
                v_type,
                v_cat,
                f"UAF-SYN-{i:04d}",
                v_sidc,
                v_echelon,
                v_status,
                v_lon,
                v_lat,
                v_osm_id,
                v_area_id,
                json.dumps({"readiness_pct": 70 + (i % 30), "callsign": f"СИНТЕТИК-{i}"}),
                created,
                now.isoformat(),
            ),
        )

    ev_cats = ["Телеметрія", "Логістика", "Зв'язок", "Інженерний моніторинг", "Метеообстановка", "Планове тренування"]
    ev_sevs = ["low", "medium", "medium", "high", "critical"]
    ev_stats = ["open", "in_progress", "resolved", "resolved", "archived"]

    for i in range(1, 161):
        v_obj_id = 1 + ((i * 7) % 80)
        cur.execute("SELECT lon, lat FROM objects WHERE id = ?", (v_obj_id,))
        olon, olat = cur.fetchone()
        v_cat = ev_cats[i % len(ev_cats)]
        v_sev = ev_sevs[(i * 5) % len(ev_sevs)]
        v_stat = ev_stats[(i * 3) % len(ev_stats)]
        ev_time = (now - timedelta(days=i % 32, hours=(i * 3) % 24)).strftime("%Y-%m-%dT%H:%M:%SZ")

        cur.execute(
            """INSERT INTO events (
                title, category, severity, status, event_time, lon, lat, object_id, description, is_synthetic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                f"Подія #{i:04d}: {v_cat} [{v_sev.upper()}]",
                v_cat,
                v_sev,
                v_stat,
                ev_time,
                round(olon + ((i % 7) - 3) * 0.015, 5),
                round(olat + ((i % 5) - 2) * 0.012, 5),
                v_obj_id,
                f"Синтетичне повідомлення моніторингу для умовного об'єкта #{v_obj_id:03d}.",
            ),
        )

    res_cats = ["Пально-мастильні матеріали", "Енергозабезпечення", "Засоби зв'язку", "Медичне майно", "Інженерне обладнання", "Транспортні засоби"]
    for i in range(1, 46):
        v_obj_id = 1 + ((i * 3) % 80)
        cur.execute("SELECT lon, lat FROM objects WHERE id = ?", (v_obj_id,))
        olon, olat = cur.fetchone()
        v_cat = res_cats[i % len(res_cats)]
        v_total = 120 + (i * 25) % 400
        v_avail = int(v_total * (0.5 + (i % 40) / 100.0))
        v_in_use = v_total - v_avail
        cur.execute(
            """INSERT INTO resources (
                name, category, total_amount, available_amount, in_use_amount, unit, condition, object_id, lon, lat, is_synthetic, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'од.', 'nominal', ?, ?, ?, 1, ?)""",
            (f"Резервний пакет #{i:03d} — {v_cat}", v_cat, v_total, v_avail, v_in_use, v_obj_id, olon, olat, now.isoformat()),
        )

    statuses = ["active", "standby", "maintenance", "relocating"]
    for i in range(1, 201):
        v_obj_id = 1 + (i % 80)
        ch_time = (now - timedelta(days=i % 32, hours=i % 12)).strftime("%Y-%m-%dT%H:%M:%SZ")
        cur.execute(
            "INSERT INTO object_status_history (object_id, previous_status, new_status, changed_at, reason, is_synthetic) VALUES (?, ?, ?, ?, ?, 1)",
            (v_obj_id, statuses[i % 4], statuses[(i + 1) % 4], ch_time, f"Планова зміна стану за графіком #{i}"),
        )

    conn.commit()
    conn.close()


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/v1/health")
def health():
    conn = get_conn()
    cnt = conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
    conn.close()
    return {
        "status": "ok",
        "database_connected": True,
        "postgis_info": "SQLite Spatial Emulation Mode (SRID 4326)",
        "objects_in_db": cnt,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/metrics/summary")
def summary_metrics(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    object_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    conn = get_conn()
    where = "WHERE 1=1"
    params = []
    if category:
        where += " AND category = ?"
        params.append(category)
    if status:
        where += " AND status = ?"
        params.append(status)
    if object_type:
        where += " AND object_type = ?"
        params.append(object_type)
    if search:
        where += " AND (name LIKE ? OR code LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    total_obj = conn.execute(f"SELECT COUNT(*) FROM objects {where}", params).fetchone()[0]
    active_obj = conn.execute(f"SELECT COUNT(*) FROM objects {where} AND status = 'active'", params).fetchone()[0]

    ev_where = f"WHERE object_id IN (SELECT id FROM objects {where})"
    ev_params = list(params)
    if severity:
        ev_where += " AND severity = ?"
        ev_params.append(severity)

    total_ev = conn.execute(f"SELECT COUNT(*) FROM events {ev_where}", ev_params).fetchone()[0]
    open_ev = conn.execute(f"SELECT COUNT(*) FROM events {ev_where} AND status IN ('open', 'in_progress')", ev_params).fetchone()[0]

    res_row = conn.execute(
        f"SELECT COALESCE(SUM(total_amount),0), COALESCE(SUM(available_amount),0) FROM resources WHERE object_id IN (SELECT id FROM objects {where})",
        params,
    ).fetchone()
    total_res, avail_res = res_row[0], res_row[1]
    pct = round(avail_res / total_res * 100.0, 1) if total_res > 0 else 0.0
    conn.close()
    return {
        "total_objects": total_obj,
        "active_objects": active_obj,
        "total_events": total_ev,
        "open_events": open_ev,
        "total_resources_units": total_res,
        "available_resources_units": avail_res,
        "resource_availability_pct": pct,
    }


@app.get("/api/v1/objects")
def get_objects(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    object_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    conn = get_conn()
    where = "WHERE 1=1"
    params = []
    if category:
        where += " AND o.category = ?"
        params.append(category)
    if status:
        where += " AND o.status = ?"
        params.append(status)
    if object_type:
        where += " AND o.object_type = ?"
        params.append(object_type)
    if search:
        where += " AND (o.name LIKE ? OR o.code LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    rows = conn.execute(
        f"""SELECT o.*, osm.name AS osm_feature_name, a.name AS area_name
            FROM objects o
            LEFT JOIN osm_features osm ON osm.osm_id = o.osm_feature_id
            LEFT JOIN areas a ON a.id = o.area_id
            {where} ORDER BY o.id ASC""",
        params,
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["longitude"] = d["lon"]
        d["latitude"] = d["lat"]
        d["attributes"] = json.loads(d["attributes"])
        result.append(d)
    return result


@app.get("/api/v1/objects/{object_id}")
def get_object_detail(object_id: int):
    conn = get_conn()
    row = conn.execute(
        """SELECT o.*, osm.name AS osm_feature_name, a.name AS area_name
           FROM objects o
           LEFT JOIN osm_features osm ON osm.osm_id = o.osm_feature_id
           LEFT JOIN areas a ON a.id = o.area_id
           WHERE o.id = ?""",
        (object_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Об'єкт не знайдено")
    hist = conn.execute(
        "SELECT * FROM object_status_history WHERE object_id = ? ORDER BY changed_at DESC LIMIT 8",
        (object_id,),
    ).fetchall()
    ev_cnt = conn.execute("SELECT COUNT(*) FROM events WHERE object_id = ?", (object_id,)).fetchone()[0]
    res_cnt = conn.execute("SELECT COUNT(*) FROM resources WHERE object_id = ?", (object_id,)).fetchone()[0]
    conn.close()
    d = dict(row)
    d["longitude"] = d["lon"]
    d["latitude"] = d["lat"]
    d["attributes"] = json.loads(d["attributes"])
    d["status_history"] = [dict(h) for h in hist]
    d["recent_events_count"] = ev_cnt
    d["assigned_resources_count"] = res_cnt
    return d


@app.get("/api/v1/events")
def get_events(category: Optional[str] = Query(None), severity: Optional[str] = Query(None)):
    conn = get_conn()
    where = "WHERE 1=1"
    params = []
    if category:
        where += " AND o.category = ?"
        params.append(category)
    if severity:
        where += " AND e.severity = ?"
        params.append(severity)
    rows = conn.execute(
        f"""SELECT e.*, o.name AS object_name, o.code AS object_code
            FROM events e LEFT JOIN objects o ON o.id = e.object_id
            {where} ORDER BY e.event_time DESC LIMIT 160""",
        params,
    ).fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        d["longitude"] = d["lon"]
        d["latitude"] = d["lat"]
        res.append(d)
    return res


@app.get("/api/v1/resources")
def get_resources():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM resources ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/v1/analytics/timeseries")
def get_timeseries():
    conn = get_conn()
    now = datetime.utcnow().date()
    points = []
    for d_offset in range(30, -1, -1):
        d_str = (now - timedelta(days=d_offset)).strftime("%Y-%m-%d")
        ev_cnt = conn.execute("SELECT COUNT(*) FROM events WHERE substr(event_time, 1, 10) = ?", (d_str,)).fetchone()[0]
        crit_cnt = conn.execute(
            "SELECT COUNT(*) FROM events WHERE substr(event_time, 1, 10) = ? AND severity IN ('high', 'critical')",
            (d_str,),
        ).fetchone()[0]
        chg_cnt = conn.execute(
            "SELECT COUNT(*) FROM object_status_history WHERE substr(changed_at, 1, 10) = ?",
            (d_str,),
        ).fetchone()[0]
        points.append({
            "date": d_str[5:],
            "events_count": ev_cnt,
            "critical_events": crit_cnt,
            "status_changes": chg_cnt,
            "readiness_index": round(84.0 + (d_offset % 11) - crit_cnt * 1.1, 1),
        })
    conn.close()
    return points


@app.get("/api/v1/analytics/categories")
def get_categories_analytics(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    object_type: Optional[str] = Query(None),
):
    conn = get_conn()
    where = "WHERE 1=1"
    params = []
    if category:
        where += " AND category = ?"
        params.append(category)
    if status:
        where += " AND status = ?"
        params.append(status)
    if object_type:
        where += " AND object_type = ?"
        params.append(object_type)

    by_cat = conn.execute(f"SELECT category AS name, COUNT(*) AS value FROM objects {where} GROUP BY category ORDER BY value DESC", params).fetchall()
    by_stat = conn.execute(f"SELECT status AS name, COUNT(*) AS value FROM objects {where} GROUP BY status ORDER BY value DESC", params).fetchall()
    by_sev = conn.execute(
        f"SELECT severity AS name, COUNT(*) AS value FROM events WHERE object_id IN (SELECT id FROM objects {where}) GROUP BY severity ORDER BY value DESC",
        params,
    ).fetchall()
    res_cmp = conn.execute(
        f"SELECT category AS name, COALESCE(SUM(available_amount),0) AS value, COALESCE(SUM(in_use_amount),0) AS extra FROM resources WHERE object_id IN (SELECT id FROM objects {where}) GROUP BY category",
        params,
    ).fetchall()
    conn.close()
    return {
        "by_category": [dict(r) for r in by_cat],
        "by_status": [dict(r) for r in by_stat],
        "by_severity": [dict(r) for r in by_sev],
        "resources_comparison": [dict(r) for r in res_cmp],
    }


@app.get("/api/v1/map/geojson")
def get_map_geojson():
    conn = get_conn()
    areas = conn.execute("SELECT * FROM areas").fetchall()
    conn.close()
    features = []
    for a in areas:
        features.append({
            "type": "Feature",
            "id": f"area-{a['id']}",
            "geometry": {"type": "Polygon", "coordinates": json.loads(a["coords_json"])},
            "properties": {
                "layer": "areas",
                "id": a["id"],
                "name": a["name"],
                "area_type": a["area_type"],
                "area_sq_km": a["area_sq_km"],
            },
        })
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/v1/osm/features")
def get_osm_features():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM osm_features").fetchall()
    conn.close()
    features = [
        {
            "type": "Feature",
            "id": f"osm-{r['osm_id']}",
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
            "properties": {"osm_id": r["osm_id"], "name": r["name"], "category": r["category"]},
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ІАС Геопросторового Моніторингу | Збройні Сили України</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/milsymbol@3.0.4/dist/milsymbol.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            uaf: {
              mundyr: '#4D4634',
              gold: '#F39200',
              step: '#6A653A',
              sky: '#293757',
              eskadra: '#111224',
              steel: '#707276',
              wave: '#035C6B',
              maroon: '#671318',
              olive: '#444A38',
              vspred: '#E52421',
              darkbg: '#1E1C16',
              panel: '#2B281F'
            }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #1E1C16; color: #F5F5F4; font-family: system-ui, -apple-system, sans-serif; }
    .leaflet-popup-content-wrapper { background: #2B281F !important; color: #F5F5F4 !important; border: 1px solid #F39200; border-radius: 4px; }
    .leaflet-popup-tip { background: #2B281F !important; }
    .milsymbol-icon { background: transparent !important; border: none !important; }
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <!-- ШАПКА У СТИЛІ БРЕНДБУКУ ЗСУ -->
  <header class="bg-uaf-mundyr border-b-2 border-uaf-gold px-6 py-3 flex flex-wrap items-center justify-between gap-4 shadow-lg">
    <div class="flex items-center gap-3.5">
      <div class="w-11 h-11 bg-uaf-mundyr border border-uaf-gold/60 flex items-center justify-center rounded-sm shrink-0">
        <svg viewBox="0 0 100 120" class="w-7 h-7 fill-uaf-gold">
          <path d="M50 6 L57 26 L56 80 L72 80 L72 34 C72 24 79 17 86 14 L86 94 L57 94 L50 114 L43 94 L14 94 L14 14 C21 17 28 24 28 34 L28 80 L44 80 L43 26 Z" />
        </svg>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase tracking-widest px-2 py-0.5 bg-uaf-gold text-black font-bold rounded-sm">Збройні Сили України</span>
          <span class="text-xs text-stone-200 border border-stone-400 px-2 py-0.5 rounded-sm">СИНТЕТИЧНІ ДАНІ (ДЕМО)</span>
        </div>
        <h1 class="text-lg md:text-xl font-bold text-white mt-0.5">Інформаційно-аналітична система геопросторового моніторингу</h1>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-3 text-xs">
      <div class="bg-uaf-darkbg/80 px-3 py-1.5 rounded border border-stone-600">
        Стан БД: <span id="db-status" class="font-bold text-emerald-400">ПІДКЛЮЧЕНО</span>
      </div>
      <a href="/docs" target="_blank" class="bg-uaf-sky hover:bg-uaf-wave text-white font-semibold px-3 py-1.5 rounded border border-stone-500 transition">Swagger API (/docs)</a>
      <div id="clock" class="bg-uaf-darkbg/80 px-3 py-1.5 rounded border border-stone-600 font-mono"></div>
      <button onclick="loadAllData()" class="bg-uaf-gold hover:bg-amber-500 text-black font-bold px-4 py-1.5 rounded transition">Оновити дані</button>
    </div>
  </header>

  <main class="flex-1 p-5 space-y-5 max-w-[1920px] w-full mx-auto">
    <!-- ПАНЕЛЬ KPI -->
    <section class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      <div class="bg-uaf-panel border-l-4 border-uaf-gold p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Усього об'єктів</div>
        <div id="kpi-total-obj" class="text-3xl font-bold text-white mt-1">—</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-step p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Активних об'єктів</div>
        <div id="kpi-active-obj" class="text-3xl font-bold text-uaf-gold mt-1">—</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-wave p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Зареєстровано подій</div>
        <div id="kpi-total-ev" class="text-3xl font-bold text-white mt-1">—</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-vspred p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Відкритих подій</div>
        <div id="kpi-open-ev" class="text-3xl font-bold text-uaf-vspred mt-1">—</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-steel p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Обсяг ресурсів (од.)</div>
        <div id="kpi-total-res" class="text-3xl font-bold text-white mt-1">—</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-gold p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Доступність ресурсів</div>
        <div id="kpi-avail-pct" class="text-3xl font-bold text-uaf-gold mt-1">—</div>
      </div>
    </section>

    <!-- ФІЛЬТРИ -->
    <section class="bg-uaf-panel border border-uaf-mundyr p-4 rounded shadow">
      <div class="flex items-center justify-between mb-3">
        <span class="text-sm font-bold text-uaf-gold uppercase tracking-wider">Наскрізні фільтри системи</span>
        <button onclick="resetFilters()" class="text-xs text-stone-300 hover:text-uaf-gold underline">Скинути всі фільтри</button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <select id="flt-category" onchange="loadAllData()" class="bg-uaf-darkbg border border-uaf-mundyr rounded px-3 py-2 text-stone-100">
          <option value="">Усі види та Сили ЗСУ</option>
          <option value="Сухопутні війська">Сухопутні війська</option>
          <option value="Повітряні Сили">Повітряні Сили</option>
          <option value="Військово-Морські Сили">Військово-Морські Сили</option>
          <option value="Десантно-штурмові війська">Десантно-штурмові війська</option>
          <option value="Сили спеціальних операцій">Сили спеціальних операцій</option>
          <option value="Сили територіальної оборони">Сили територіальної оборони</option>
          <option value="Морська піхота">Морська піхота</option>
          <option value="Військова служба правопорядку">Військова служба правопорядку</option>
        </select>
        <select id="flt-status" onchange="loadAllData()" class="bg-uaf-darkbg border border-uaf-mundyr rounded px-3 py-2 text-stone-100">
          <option value="">Усі статуси об'єктів</option>
          <option value="active">Активний (active)</option>
          <option value="standby">Резерв (standby)</option>
          <option value="maintenance">Обслуговування (maintenance)</option>
          <option value="relocating">Переміщення (relocating)</option>
        </select>
        <select id="flt-severity" onchange="loadAllData()" class="bg-uaf-darkbg border border-uaf-mundyr rounded px-3 py-2 text-stone-100">
          <option value="">Усі рівні важливості подій</option>
          <option value="critical">Критичний (critical)</option>
          <option value="high">Високий (high)</option>
          <option value="medium">Середній (medium)</option>
          <option value="low">Низький (low)</option>
        </select>
        <input id="flt-search" oninput="loadAllData()" type="text" placeholder="Пошук за кодом UAF-SYN або назвою..." class="bg-uaf-darkbg border border-uaf-mundyr rounded px-3 py-2 text-stone-100" />
      </div>
    </section>

    <!-- КАРТА LEAFLET + MILSYMBOL ТА ПАСПОРТ ОБ'ЄКТА -->
    <section class="grid grid-cols-1 lg:grid-cols-4 gap-5">
      <div class="lg:col-span-3 relative rounded border border-uaf-mundyr overflow-hidden shadow-lg bg-uaf-eskadra">
        <div id="map" class="w-full h-[540px] z-10"></div>
        <!-- Легенда milsymbol -->
        <div class="absolute bottom-6 left-3 z-[1000] bg-uaf-panel/95 border border-uaf-mundyr p-3 rounded shadow-md text-xs max-w-xs">
          <div class="font-bold text-uaf-gold uppercase border-b border-uaf-mundyr pb-1 mb-2">Легенда milsymbol (APP-6)</div>
          <div id="legend-list" class="space-y-1.5"></div>
        </div>
      </div>

      <!-- Панель вибраного об'єкта -->
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow flex flex-col justify-between">
        <div id="detail-box" class="space-y-3 text-xs">
          <div class="text-center py-16 text-stone-400">
            Натисніть на будь-який військовий знак <b>milsymbol</b> на карті або кнопку «На карті» в таблиці нижче для перегляду паспорта об'єкта та історії його станів.
          </div>
        </div>
        <div class="pt-3 border-t border-uaf-mundyr text-[11px] text-stone-400 flex justify-between">
          <span>is_synthetic = true</span>
          <span class="text-uaf-gold font-bold">zsu.gov.ua</span>
        </div>
      </div>
    </section>

    <!-- 6 АНАЛІТИЧНИХ ГРАФІКІВ -->
    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">1. Динаміка кількості подій (30 діб)</h3>
        <div class="h-56"><canvas id="chart-events-ts"></canvas></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">2. Розподіл об'єктів за видами та Силами ЗСУ</h3>
        <div class="h-56"><canvas id="chart-categories"></canvas></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">3. Розподіл об'єктів за статусами</h3>
        <div class="h-56"><canvas id="chart-statuses"></canvas></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">4. Динаміка індексу готовності та змін стану</h3>
        <div class="h-56"><canvas id="chart-readiness"></canvas></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">5. Співвідношення доступних і задіяних ресурсів</h3>
        <div class="h-56"><canvas id="chart-resources"></canvas></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow">
        <h3 class="text-xs font-bold text-uaf-gold uppercase mb-2">6. Розподіл подій за рівнями важливості</h3>
        <div class="h-56"><canvas id="chart-severity"></canvas></div>
      </div>
    </section>

    <!-- ТАБЛИЦЯ ОБ'ЄКТІВ -->
    <section class="bg-uaf-panel border border-uaf-mundyr rounded shadow overflow-hidden">
      <div class="px-4 py-3 border-b border-uaf-mundyr flex justify-between items-center">
        <h2 class="text-sm font-bold text-uaf-gold uppercase">Реєстр умовних геопросторових об'єктів (<span id="table-count">0</span>)</h2>
        <span class="text-xs text-stone-400">Координати WGS 84 (SRID 4326)</span>
      </div>
      <div class="overflow-x-auto max-h-96">
        <table class="w-full text-left border-collapse text-xs">
          <thead class="bg-uaf-mundyr text-stone-200 sticky top-0">
            <tr>
              <th class="p-3">Знак milsymbol</th>
              <th class="p-3">Код</th>
              <th class="p-3">Назва умовного об'єкта</th>
              <th class="p-3">Вид / Рід Сил</th>
              <th class="p-3">Статус</th>
              <th class="p-3">Орієнтир OSM</th>
              <th class="p-3">Координати</th>
              <th class="p-3 text-right">Позиціонування</th>
            </tr>
          </thead>
          <tbody id="objects-tbody" class="divide-y divide-uaf-mundyr/60"></tbody>
        </table>
      </div>
    </section>
  </main>

  <script>
    const UAF_COLORS = ['#F39200', '#6A653A', '#035C6B', '#293757', '#671318', '#707276', '#444A38', '#E52421'];
    let map, markersLayer, eventsLayer, areasLayer, osmLayer;
    let charts = {};

    setInterval(() => {
      document.getElementById('clock').textContent = new Date().toLocaleString('uk-UA');
    }, 1000);
    document.getElementById('clock').textContent = new Date().toLocaleString('uk-UA');

    function makeMilsymbolSvg(sidc, size = 28, designation = '') {
      const s = new ms.Symbol(sidc || 'SFGPUCI---F----', {
        size: size,
        uniqueDesignation: designation,
        infoFields: Boolean(designation),
        outlineWidth: 2,
        outlineColor: '#1E1C16'
      });
      return s.asSVG();
    }

    function initMap() {
      map = L.map('map').setView([48.537, 31.168], 7);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>'
      }).addTo(map);

      areasLayer = L.layerGroup().addTo(map);
      osmLayer = L.layerGroup().addTo(map);
      eventsLayer = L.layerGroup().addTo(map);
      markersLayer = L.layerGroup().addTo(map);

      L.control.layers(null, {
        "Умовні об'єкти (milsymbol)": markersLayer,
        "Синтетичні події": eventsLayer,
        "Зони моніторингу": areasLayer,
        "Орієнтири OpenStreetMap": osmLayer
      }, { collapsed: false }).addTo(map);

      const legendItems = [
        { label: 'Пункт управління', sidc: 'SFGPE-----F----' },
        { label: 'Механізований підрозділ', sidc: 'SFGPUCI---F----' },
        { label: 'Підрозділ ППО', sidc: 'SFGPUCD---F----' },
        { label: 'Логістичний вузол', sidc: 'SFGPUSS---F----' },
        { label: "Вузол зв'язку", sidc: 'SFGPUSM---F----' }
      ];
      document.getElementById('legend-list').innerHTML = legendItems.map(i => `
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 flex items-center justify-center">${makeMilsymbolSvg(i.sidc, 20)}</div>
          <div>
            <div class="font-medium text-stone-100">${i.label}</div>
            <div class="text-[10px] font-mono text-stone-400">${i.sidc}</div>
          </div>
        </div>
      `).join('');
    }

    function resetFilters() {
      document.getElementById('flt-category').value = '';
      document.getElementById('flt-status').value = '';
      document.getElementById('flt-severity').value = '';
      document.getElementById('flt-search').value = '';
      loadAllData();
    }

    async function selectObject(id) {
      const res = await fetch(`/api/v1/objects/${id}`);
      const d = await res.json();
      map.flyTo([d.latitude, d.longitude], 10, { duration: 1.0 });

      const histHtml = (d.status_history || []).map(h => `
        <div class="bg-uaf-darkbg p-2 rounded border-l-2 border-uaf-gold text-[11px]">
          <div class="flex justify-between font-mono">
            <span>${h.previous_status} &rarr; <b>${h.new_status}</b></span>
            <span>${h.changed_at.slice(0, 10)}</span>
          </div>
          <div class="text-stone-400">${h.reason}</div>
        </div>
      `).join('');

      document.getElementById('detail-box').innerHTML = `
        <div class="flex items-start justify-between border-b border-uaf-mundyr pb-2">
          <div>
            <span class="font-mono bg-uaf-mundyr text-uaf-gold px-2 py-0.5 rounded">${d.code}</span>
            <h3 class="text-sm font-bold text-white mt-1">${d.name}</h3>
          </div>
          <div class="w-12 h-12 flex items-center justify-center bg-uaf-darkbg rounded border border-uaf-mundyr">
            ${makeMilsymbolSvg(d.sidc, 30)}
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div class="bg-uaf-darkbg p-2 rounded"><span class="text-stone-400 block">Вид/Сили:</span><b>${d.category}</b></div>
          <div class="bg-uaf-darkbg p-2 rounded"><span class="text-stone-400 block">Статус:</span><b class="text-uaf-gold uppercase">${d.status}</b></div>
          <div class="bg-uaf-darkbg p-2 rounded"><span class="text-stone-400 block">SIDC:</span><b class="font-mono">${d.sidc}</b></div>
          <div class="bg-uaf-darkbg p-2 rounded"><span class="text-stone-400 block">OSM орієнтир:</span><b class="text-sky-400">${d.osm_feature_name || '—'}</b></div>
        </div>
        <div class="bg-uaf-darkbg p-2 rounded">
          <div>Зона: <b>${d.area_name || '—'}</b></div>
          <div>Координати: <b>${d.latitude.toFixed(4)}° N, ${d.longitude.toFixed(4)}° E</b></div>
          <div>Подій: <b>${d.recent_events_count}</b> | Ресурсів: <b>${d.assigned_resources_count}</b></div>
        </div>
        <div class="font-bold text-uaf-gold uppercase pt-1">Історія зміни станів:</div>
        <div class="space-y-1.5 max-h-44 overflow-y-auto">${histHtml}</div>
      `;
    }

    function renderChart(id, config) {
      if (charts[id]) charts[id].destroy();
      charts[id] = new Chart(document.getElementById(id), config);
    }

    async function loadAllData() {
      const category = document.getElementById('flt-category').value;
      const status = document.getElementById('flt-status').value;
      const severity = document.getElementById('flt-severity').value;
      const search = document.getElementById('flt-search').value;

      const qs = new URLSearchParams();
      if (category) qs.set('category', category);
      if (status) qs.set('status', status);
      if (severity) qs.set('severity', severity);
      if (search) qs.set('search', search);

      const [sumRes, objRes, evRes, tsRes, catRes, geoRes, osmRes] = await Promise.all([
        fetch(`/api/v1/metrics/summary?${qs}`).then(r => r.json()),
        fetch(`/api/v1/objects?${qs}`).then(r => r.json()),
        fetch(`/api/v1/events?${qs}`).then(r => r.json()),
        fetch(`/api/v1/analytics/timeseries`).then(r => r.json()),
        fetch(`/api/v1/analytics/categories?${qs}`).then(r => r.json()),
        fetch(`/api/v1/map/geojson`).then(r => r.json()),
        fetch(`/api/v1/osm/features`).then(r => r.json()),
      ]);

      document.getElementById('kpi-total-obj').textContent = sumRes.total_objects;
      document.getElementById('kpi-active-obj').textContent = sumRes.active_objects;
      document.getElementById('kpi-total-ev').textContent = sumRes.total_events;
      document.getElementById('kpi-open-ev').textContent = sumRes.open_events;
      document.getElementById('kpi-total-res').textContent = sumRes.total_resources_units;
      document.getElementById('kpi-avail-pct').textContent = sumRes.resource_availability_pct + '%';

      markersLayer.clearLayers();
      eventsLayer.clearLayers();
      areasLayer.clearLayers();
      osmLayer.clearLayers();

      (geoRes.features || []).forEach(f => {
        const latlngs = f.geometry.coordinates[0].map(c => [c[1], c[0]]);
        L.polygon(latlngs, { color: '#F39200', weight: 1.5, fillColor: '#4D4634', fillOpacity: 0.18 })
          .bindPopup(`<b>${f.properties.name}</b><br>Площа: ${f.properties.area_sq_km} км²`)
          .addTo(areasLayer);
      });

      (osmRes.features || []).forEach(f => {
        const [lon, lat] = f.geometry.coordinates;
        L.circleMarker([lat, lon], { radius: 5, color: '#293757', fillColor: '#38BDF8', fillOpacity: 0.85 })
          .bindPopup(`<b>OSM: ${f.properties.name}</b>`)
          .addTo(osmLayer);
      });

      evRes.slice(0, 80).forEach(ev => {
        const col = ev.severity === 'critical' ? '#E52421' : ev.severity === 'high' ? '#F39200' : '#035C6B';
        L.circleMarker([ev.latitude, ev.longitude], { radius: 5, color: '#111224', fillColor: col, fillOpacity: 0.9 })
          .bindPopup(`<b>${ev.title}</b><br>${ev.description}`)
          .addTo(eventsLayer);
      });

      objRes.forEach(o => {
        const sym = new ms.Symbol(o.sidc, { size: 28, uniqueDesignation: o.code.replace('UAF-SYN-', ''), infoFields: true });
        const anchor = sym.getAnchor();
        const sz = sym.getSize();
        const icon = L.divIcon({
          className: 'milsymbol-icon',
          html: sym.asSVG(),
          iconSize: [sz.width, sz.height],
          iconAnchor: [anchor.x, anchor.y]
        });
        const m = L.marker([o.latitude, o.longitude], { icon })
          .bindPopup(`<b>${o.name}</b><br>Код: ${o.code}<br>Статус: ${o.status}`)
          .on('click', () => selectObject(o.id));
        m.addTo(markersLayer);
      });

      document.getElementById('table-count').textContent = objRes.length;
      document.getElementById('objects-tbody').innerHTML = objRes.map(o => `
        <tr class="hover:bg-uaf-mundyr/40">
          <td class="p-2.5"><div class="w-8 h-8 flex items-center justify-center">${makeMilsymbolSvg(o.sidc, 22)}</div></td>
          <td class="p-2.5 font-mono font-bold text-uaf-gold">${o.code}</td>
          <td class="p-2.5 text-white">${o.name}</td>
          <td class="p-2.5">${o.category}</td>
          <td class="p-2.5 uppercase font-semibold text-uaf-gold">${o.status}</td>
          <td class="p-2.5 text-sky-400">${o.osm_feature_name || '—'}</td>
          <td class="p-2.5 font-mono">${o.latitude.toFixed(4)}, ${o.longitude.toFixed(4)}</td>
          <td class="p-2.5 text-right">
            <button onclick="selectObject(${o.id})" class="bg-uaf-gold hover:bg-amber-500 text-black font-bold px-2.5 py-1 rounded-sm">На карті</button>
          </td>
        </tr>
      `).join('');

      const commonOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#D6D3D1', font: { size: 10 } } } }, scales: { x: { ticks: { color: '#D6D3D1', font: { size: 10 } } }, y: { ticks: { color: '#D6D3D1', font: { size: 10 } } } } };

      renderChart('chart-events-ts', {
        type: 'line',
        data: {
          labels: tsRes.map(x => x.date),
          datasets: [
            { label: 'Усього подій', data: tsRes.map(x => x.events_count), borderColor: '#F39200', backgroundColor: 'rgba(243,146,0,0.25)', fill: true },
            { label: 'Критичні', data: tsRes.map(x => x.critical_events), borderColor: '#E52421', backgroundColor: 'rgba(229,36,33,0.3)', fill: true }
          ]
        },
        options: commonOpts
      });

      renderChart('chart-categories', {
        type: 'bar',
        data: {
          labels: catRes.by_category.map(x => x.name),
          datasets: [{ label: "Кількість об'єктів", data: catRes.by_category.map(x => x.value), backgroundColor: UAF_COLORS }]
        },
        options: { ...commonOpts, indexAxis: 'y' }
      });

      renderChart('chart-statuses', {
        type: 'doughnut',
        data: {
          labels: catRes.by_status.map(x => x.name),
          datasets: [{ data: catRes.by_status.map(x => x.value), backgroundColor: UAF_COLORS }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#D6D3D1' } } } }
      });

      renderChart('chart-readiness', {
        type: 'line',
        data: {
          labels: tsRes.map(x => x.date),
          datasets: [
            { label: 'Індекс готовності (%)', data: tsRes.map(x => x.readiness_index), borderColor: '#F39200' },
            { label: 'Зміни станів', data: tsRes.map(x => x.status_changes), borderColor: '#035C6B' }
          ]
        },
        options: commonOpts
      });

      renderChart('chart-resources', {
        type: 'bar',
        data: {
          labels: catRes.resources_comparison.map(x => x.name),
          datasets: [
            { label: 'Доступно', data: catRes.resources_comparison.map(x => x.value), backgroundColor: '#6A653A' },
            { label: 'У використанні', data: catRes.resources_comparison.map(x => x.extra), backgroundColor: '#F39200' }
          ]
        },
        options: commonOpts
      });

      renderChart('chart-severity', {
        type: 'bar',
        data: {
          labels: catRes.by_severity.map(x => x.name),
          datasets: [{ label: 'Події', data: catRes.by_severity.map(x => x.value), backgroundColor: ['#F39200', '#035C6B', '#E52421', '#6A653A'] }]
        },
        options: commonOpts
      });
    }

    window.addEventListener('DOMContentLoaded', () => {
      initMap();
      loadAllData();
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    return DASHBOARD_HTML


if __name__ == "__main__":
    print("Ініціалізація локальної бази даних та синтетичних об'єктів...")
    init_sqlite_db()
    url = "http://localhost:8000"
    print(f"Сервер запущено! Відкриваю дашборд у браузері: {url}")
    print(f"Swagger документація API: {url}/docs")
    Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)