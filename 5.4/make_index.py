from pathlib import Path
import run_local

print("Ініціалізація бази даних та генерація index.html...")
run_local.init_sqlite_db()

# Отримуємо дані з локальної БД SQLite
data = {
    "objects": run_local.get_objects(),
    "events": run_local.get_events(),
    "ts": run_local.get_timeseries(),
    "cat": run_local.get_categories_analytics(),
    "geo": run_local.get_map_geojson(),
    "osm": run_local.get_osm_features(),
}

# Вшиваємо дані та мок-сервер прямо у HTML
patch = f"""<script>
const EMBEDDED = {run_local.json.dumps(data, ensure_ascii=False)};
const _f = window.fetch;
window.fetch = async (u) => {{
  u = String(u);
  const p = new URL(u, location.origin).searchParams;
  const c = p.get("category") || "", s = p.get("status") || "", v = p.get("severity") || "", q = (p.get("search") || "").toLowerCase();
  const objs = EMBEDDED.objects.filter(o => (!c || o.category === c) && (!s || o.status === s) && (!q || o.name.toLowerCase().includes(q) || o.code.toLowerCase().includes(q)));
  const ids = new Set(objs.map(o => o.id));
  const evs = EMBEDDED.events.filter(e => ids.has(e.object_id) && (!v || e.severity === v));
  
  if (u.includes("/metrics/summary")) return {{ json: async () => ({{"total_objects": objs.length, "active_objects": objs.filter(o => o.status === "active").length, "total_events": evs.length, "open_events": evs.filter(e => e.status === "open" || e.status === "in_progress").length, "total_resources_units": 9850, "available_resources_units": 6720, "resource_availability_pct": 68.2}}) }};
  if (u.includes("/objects/")) {{
    const id = Number(u.split("/objects/")[1]);
    const o = EMBEDDED.objects.find(x => x.id === id) || EMBEDDED.objects[0];
    return {{ json: async () => ({{ ...o, "recent_events_count": 3, "assigned_resources_count": 2, "status_history": [{{"previous_status": "standby", "new_status": o.status, "changed_at": "2026-03-25", "reason": "Планова перевірка готовності"}}] }}) }};
  }}
  if (u.includes("/objects")) return {{ json: async () => objs }};
  if (u.includes("/events")) return {{ json: async () => evs }};
  if (u.includes("/timeseries")) return {{ json: async () => EMBEDDED.ts }};
  if (u.includes("/categories")) {{
    const bc = {{}}, bs = {{}}, bv = {{}};
    objs.forEach(o => {{ bc[o.category] = (bc[o.category] || 0) + 1; bs[o.status] = (bs[o.status] || 0) + 1; }});
    evs.forEach(e => {{ bv[e.severity] = (bv[e.severity] || 0) + 1; }});
    return {{ json: async () => ({{ "by_category": Object.entries(bc).map(([name, value]) => ({{name, value}})), "by_status": Object.entries(bs).map(([name, value]) => ({{name, value}})), "by_severity": Object.entries(bv).map(([name, value]) => ({{name, value}})), "resources_comparison": EMBEDDED.cat.resources_comparison }}) }};
  }}
  if (u.includes("/geojson")) return {{ json: async () => EMBEDDED.geo }};
  if (u.includes("/osm/features")) return {{ json: async () => EMBEDDED.osm }};
  return _f(u);
}};
</script>
</head>"""

final_html = run_local.DASHBOARD_HTML.replace("</head>", patch)
Path("index.html").write_text(final_html, encoding="utf-8")
print("Успішно створено автономний файл index.html!")