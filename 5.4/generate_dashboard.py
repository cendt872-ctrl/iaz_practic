import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("local_geo_analytics.db")

print("Ініціалізація локальної бази даних та наповнення синтетичними даними...")
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.executescript("""
CREATE TABLE osm_features (
    osm_id INTEGER PRIMARY KEY,
    osm_type TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    lon REAL NOT NULL,
    lat REAL NOT NULL,
    tags TEXT NOT NULL
);

CREATE TABLE areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    area_type TEXT NOT NULL,
    coords_json TEXT NOT NULL,
    area_sq_km REAL NOT NULL
);

CREATE TABLE objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    object_type TEXT NOT NULL,
    category TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    sidc TEXT NOT NULL,
    status TEXT NOT NULL,
    lon REAL NOT NULL,
    lat REAL NOT NULL,
    osm_feature_id INTEGER,
    area_id INTEGER,
    attributes TEXT NOT NULL
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
    description TEXT NOT NULL
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
    object_id INTEGER
);

CREATE TABLE object_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    previous_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_at TEXT NOT NULL,
    reason TEXT NOT NULL
);
""")

now = datetime.utcnow()
for oid, otype, name, cat, lon, lat in [
    (26150422, "node", "Кропивницький", "city", 32.2623, 48.5079),
    (25870505, "node", "Черкаси", "city", 32.0588, 49.4444),
    (26150198, "node", "Вінниця", "city", 28.4682, 49.2331),
    (26150301, "node", "Полтава", "city", 34.5514, 49.5883),
    (31490011, "node", "Умань", "town", 30.2218, 48.7484),
    (31490012, "node", "Олександрія", "town", 33.1169, 48.6696),
]:
    cur.execute("INSERT INTO osm_features VALUES (?, ?, ?, ?, ?, ?, ?)", (oid, otype, name, cat, lon, lat, "{}"))

cur.execute(
    "INSERT INTO areas (name, area_type, coords_json, area_sq_km) VALUES (?, ?, ?, ?)",
    ("Сектор моніторингу «Центр-Північ»", "monitoring_zone", json.dumps([[[29.50, 49.90], [32.20, 49.90], [32.20, 48.80], [29.50, 48.80], [29.50, 49.90]]]), 24180.5)
)

types_arr = ["command_post", "mechanized_unit", "air_defense", "logistics_hub", "comms_node", "radar_station"]
cats_arr = ["Сухопутні війська", "Повітряні Сили", "Військово-Морські Сили", "Десантно-штурмові війська", "Сили спеціальних операцій", "Сили територіальної оборони", "Морська піхота", "Військова служба правопорядку"]
sidc_arr = ["SFGPE-----F----", "SFGPUCI---F----", "SFGPUCD---F----", "SFGPUSS---F----", "SFGPUSM---F----", "SFGPUCF---F----"]
status_arr = ["active", "active", "standby", "maintenance", "relocating"]

for i in range(1, 76):
    v_type = types_arr[i % len(types_arr)]
    v_cat = cats_arr[i % len(cats_arr)]
    v_sidc = sidc_arr[i % len(sidc_arr)]
    v_status = status_arr[i % len(status_arr)]
    v_lon = round(28.15 + ((i * 37) % 650) / 100.0, 5)
    v_lat = round(47.75 + ((i * 53) % 240) / 100.0, 5)
    cur.execute(
        "INSERT INTO objects (name, object_type, category, code, sidc, status, lon, lat, osm_feature_id, area_id, attributes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)",
        (f"Умовний об'єкт #{i:03d} ({v_cat})", v_type, v_cat, f"UAF-SYN-{i:04d}", v_sidc, v_status, v_lon, v_lat, json.dumps({"readiness_pct": 75 + (i % 25)}))
    )

for i in range(1, 151):
    ev_time = (now - timedelta(days=i % 30, hours=i % 24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur.execute(
        "INSERT INTO events (title, category, severity, status, event_time, lon, lat, object_id, description) VALUES (?, ?, ?, ?, ?, 30.5, 48.6, ?, ?)",
        (f"Подія #{i:04d}", "Телеметрія", ("low", "medium", "high", "critical")[i % 4], "open", ev_time, 1 + (i % 75), "Синтетичне повідомлення моніторингу.")
    )

for i in range(1, 40):
    cur.execute("INSERT INTO resources (name, category, total_amount, available_amount, in_use_amount, unit, condition, object_id) VALUES (?, ?, 300, 180, 120, 'од.', 'nominal', ?)", (f"Пакет #{i}", "Пально-мастильні матеріали", 1 + (i % 75)))
for i in range(1, 100):
    cur.execute("INSERT INTO object_status_history (object_id, previous_status, new_status, changed_at, reason) VALUES (?, 'standby', 'active', '2026-03-25', 'Планова ротація')", (1 + (i % 75),))

conn.commit()

objects = [dict(r) for r in conn.execute("SELECT o.*, osm.name AS osm_feature_name, a.name AS area_name FROM objects o LEFT JOIN osm_features osm ON osm.osm_id = o.osm_feature_id LEFT JOIN areas a ON a.id = o.area_id").fetchall()]
for o in objects:
    o["longitude"] = o["lon"]
    o["latitude"] = o["lat"]
    o["attributes"] = json.loads(o["attributes"])

events = [dict(r) for r in conn.execute("SELECT e.*, o.name AS object_name, o.code AS object_code FROM events e LEFT JOIN objects o ON o.id = e.object_id").fetchall()]
for e in events:
    e["longitude"] = e["lon"]
    e["latitude"] = e["lat"]

areas = [dict(r) for r in conn.execute("SELECT * FROM areas").fetchall()]
osm = [dict(r) for r in conn.execute("SELECT * FROM osm_features").fetchall()]
conn.close()

# Зберігаємо дані окремо у data.json для швидкого завантаження дашбордом
Path("data.json").write_text(json.dumps({"objects": objects, "events": events, "areas": areas, "osm": osm}, ensure_ascii=False, indent=2), encoding="utf-8")

# Чистий і надійний HTML-дашборд
html_content = """<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ІАС Геопросторового Моніторингу | Збройні Сили України</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/milsymbol@3.0.4/dist/milsymbol.js"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            uaf: {
              mundyr: '#4D4634', gold: '#F39200', step: '#6A653A', sky: '#293757',
              eskadra: '#111224', steel: '#707276', wave: '#035C6B', maroon: '#671318',
              olive: '#444A38', vspred: '#E52421', darkbg: '#1E1C16', panel: '#2B281F'
            }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #1E1C16; color: #F5F5F4; font-family: system-ui, sans-serif; }
    .leaflet-popup-content-wrapper { background: #2B281F !important; color: #F5F5F4 !important; border: 1px solid #F39200; border-radius: 4px; }
    .leaflet-popup-tip { background: #2B281F !important; }
    .milsymbol-icon { background: transparent !important; border: none !important; }
  </style>
</head>
<body class="min-h-screen flex flex-col">
  <header class="bg-uaf-mundyr border-b-2 border-uaf-gold px-6 py-3 flex items-center justify-between shadow-lg">
    <div class="flex items-center gap-3.5">
      <div class="w-11 h-11 bg-uaf-mundyr border border-uaf-gold/60 flex items-center justify-center rounded-sm">
        <svg viewBox="0 0 100 120" class="w-7 h-7 fill-uaf-gold"><path d="M50 6 L57 26 L56 80 L72 80 L72 34 C72 24 79 17 86 14 L86 94 L57 94 L50 114 L43 94 L14 94 L14 14 C21 17 28 24 28 34 L28 80 L44 80 L43 26 Z" /></svg>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase px-2 py-0.5 bg-uaf-gold text-black font-bold rounded-sm">Збройні Сили України</span>
          <span class="text-xs text-stone-200 border border-stone-400 px-2 py-0.5 rounded-sm">АВТОНОМНИЙ КОНТУР</span>
        </div>
        <h1 class="text-lg font-bold text-white mt-0.5">Інформаційно-аналітична система геопросторового моніторингу</h1>
      </div>
    </div>
    <div class="text-xs bg-uaf-darkbg/80 px-3 py-1.5 rounded border border-stone-600 font-mono" id="clock"></div>
  </header>

  <main class="flex-1 p-5 space-y-5 max-w-[1920px] w-full mx-auto">
    <section class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-uaf-panel border-l-4 border-uaf-gold p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Усього об'єктів</div>
        <div id="kpi-total" class="text-3xl font-bold text-white mt-1">0</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-step p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Активних об'єктів</div>
        <div id="kpi-active" class="text-3xl font-bold text-uaf-gold mt-1">0</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-wave p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Зареєстровано подій</div>
        <div id="kpi-events" class="text-3xl font-bold text-white mt-1">0</div>
      </div>
      <div class="bg-uaf-panel border-l-4 border-uaf-steel p-4 rounded shadow">
        <div class="text-xs text-stone-400 uppercase">Ресурсні пакети</div>
        <div class="text-3xl font-bold text-white mt-1">40 од.</div>
      </div>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-4 gap-5">
      <div class="lg:col-span-3 relative rounded border border-uaf-mundyr overflow-hidden shadow-lg bg-uaf-eskadra">
        <div id="map" class="w-full h-[540px] z-10"></div>
      </div>
      <div class="bg-uaf-panel border border-uaf-mundyr rounded p-4 shadow flex flex-col justify-between">
        <div id="detail-box" class="space-y-3 text-xs text-stone-300">
          <div class="text-center py-16 text-stone-400">Натисніть на будь-який умовний знак <b>milsymbol</b> на карті для перегляду деталей об'єкта.</div>
        </div>
        <div class="pt-3 border-t border-uaf-mundyr text-[11px] text-stone-400 flex justify-between">
          <span>is_synthetic = true</span><span class="text-uaf-gold font-bold">zsu.gov.ua</span>
        </div>
      </div>
    </section>

    <section class="bg-uaf-panel border border-uaf-mundyr rounded shadow overflow-hidden">
      <div class="px-4 py-3 border-b border-uaf-mundyr font-bold text-uaf-gold uppercase text-xs">Реєстр об'єктів</div>
      <div class="overflow-x-auto max-h-80">
        <table class="w-full text-left border-collapse text-xs">
          <thead class="bg-uaf-mundyr text-stone-200 sticky top-0">
            <tr>
              <th class="p-3">Знак milsymbol</th>
              <th class="p-3">Код</th>
              <th class="p-3">Назва</th>
              <th class="p-3">Вид / Сили</th>
              <th class="p-3">Статус</th>
              <th class="p-3">Координати</th>
              <th class="p-3 text-right">Дія</th>
            </tr>
          </thead>
          <tbody id="tbody" class="divide-y divide-uaf-mundyr/60"></tbody>
        </table>
      </div>
    </section>
  </main>

  <script>
    let DATA = { objects: [], events: [], areas: [], osm: [] };

    setInterval(() => { document.getElementById('clock').textContent = new Date().toLocaleString('uk-UA'); }, 1000);
    document.getElementById('clock').textContent = new Date().toLocaleString('uk-UA');

    function makeSvg(sidc, size = 26) {
      return new ms.Symbol(sidc || 'SFGPUCI---F----', { size, outlineWidth: 2, outlineColor: '#1E1C16' }).asSVG();
    }

    const map = L.map('map').setView([48.537, 31.168], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    async function initDashboard() {
      const res = await fetch('data.json');
      DATA = await res.json();

      DATA.areas.forEach(a => {
        const coords = JSON.parse(a.coords_json)[0].map(c => [c[1], c[0]]);
        L.polygon(coords, { color: '#F39200', weight: 1.5, fillColor: '#4D4634', fillOpacity: 0.18 }).addTo(map);
      });

      DATA.objects.forEach(o => {
        const sym = new ms.Symbol(o.sidc, { size: 28, uniqueDesignation: o.code.replace('UAF-SYN-', ''), infoFields: true });
        const anchor = sym.getAnchor();
        const sz = sym.getSize();
        const icon = L.divIcon({ className: 'milsymbol-icon', html: sym.asSVG(), iconSize: [sz.width, sz.height], iconAnchor: [anchor.x, anchor.y] });
        L.marker([o.latitude, o.longitude], { icon })
          .bindPopup(`<b>${o.name}</b><br>Код: ${o.code}<br>Статус: ${o.status}`)
          .on('click', () => {
            map.flyTo([o.latitude, o.longitude], 10, { duration: 1.0 });
            document.getElementById('detail-box').innerHTML = `
              <div class="flex items-start justify-between border-b border-uaf-mundyr pb-2">
                <div><span class="font-mono bg-uaf-mundyr text-uaf-gold px-2 py-0.5 rounded">${o.code}</span><h3 class="text-sm font-bold text-white mt-1">${o.name}</h3></div>
                <div class="w-12 h-12 flex items-center justify-center bg-uaf-darkbg rounded border border-uaf-mundyr">${makeSvg(o.sidc, 32)}</div>
              </div>
              <div>Вид/Сили: <b>${o.category}</b></div>
              <div>Статус: <b class="text-uaf-gold uppercase">${o.status}</b></div>
              <div>SIDC: <b class="font-mono">${o.sidc}</b></div>
              <div>Координати: <b>${o.latitude.toFixed(4)}° N, ${o.longitude.toFixed(4)}° E</b></div>
            `;
          })
          .addTo(map);
      });

      document.getElementById('kpi-total').textContent = DATA.objects.length;
      document.getElementById('kpi-active').textContent = DATA.objects.filter(o => o.status === 'active').length;
      document.getElementById('kpi-events').textContent = DATA.events.length;

      document.getElementById('tbody').innerHTML = DATA.objects.map(o => `
        <tr class="hover:bg-uaf-mundyr/40">
          <td class="p-2.5"><div class="w-8 h-8 flex items-center justify-center">${makeSvg(o.sidc, 22)}</div></td>
          <td class="p-2.5 font-mono font-bold text-uaf-gold">${o.code}</td>
          <td class="p-2.5 text-white">${o.name}</td>
          <td class="p-2.5">${o.category}</td>
          <td class="p-2.5 uppercase font-semibold text-uaf-gold">${o.status}</td>
          <td class="p-2.5 font-mono">${o.latitude.toFixed(4)}, ${o.longitude.toFixed(4)}</td>
          <td class="p-2.5 text-right">
            <button onclick="map.flyTo([${o.latitude}, ${o.longitude}], 10)" class="bg-uaf-gold hover:bg-amber-500 text-black font-bold px-2.5 py-1 rounded-sm">На карті</button>
          </td>
        </tr>
      `).join('');
    }

    window.addEventListener('DOMContentLoaded', initDashboard);
  </script>
</body>
</html>
"""

Path("index.html").write_text(html_content, encoding="utf-8")
print("Успішно створено файл index.html та data.json!")
print("Тепер відкрийте index.html через локальний сервер (або подвійним кліком через python -m http.server 8000).")