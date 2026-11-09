import json, logging, os, httpx, psycopg2
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = '[out:json][timeout:25];(node["place"~"city|town"](47.8,29.8,49.6,33.5););out body 35;'
def main():
    conn = psycopg2.connect(host=os.getenv("POSTGRES_HOST", "localhost"), port=int(os.getenv("POSTGRES_PORT", "5432")), dbname=os.getenv("POSTGRES_DB", "geo_analytics"), user=os.getenv("POSTGRES_USER", "uaf_admin"), password=os.getenv("POSTGRES_PASSWORD", "uaf_secure_pass_2026"))
    cur = conn.cursor()
    try:
        with httpx.Client(headers={"User-Agent": "UAF-GeoAnalytics-Demo/1.0"}, timeout=25.0) as client:
            res = client.post(OVERPASS_URL, data={"data": OVERPASS_QUERY})
            res.raise_for_status()
            for el in res.json().get("elements", []):
                osm_id, lon, lat = el.get("id"), el.get("lon"), el.get("lat")
                tags = el.get("tags", {})
                name = tags.get("name:uk") or tags.get("name")
                if osm_id and lon and lat and name:
                    cur.execute("INSERT INTO osm_features (osm_id, osm_type, name, category, geom, tags, is_synthetic) VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s::jsonb, FALSE) ON CONFLICT (osm_id) DO NOTHING;", (osm_id, "node", name, tags.get("place", "town"), float(lon), float(lat), json.dumps(tags)))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.warning("Fallback to built-in OSM features: %s", e)
    finally:
        cur.close()
        conn.close()
if __name__ == "__main__":
    main()