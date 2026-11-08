import os
import webbrowser
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# 1. ГЕНЕРАЦІЯ СТАТИЧНИХ ЗВІТНИХ ГРАФІКІВ (PNG) — ВАРІАНТИ 1–10
# ==============================================================================
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
fig = plt.figure(figsize=(16, 10), facecolor='#f8fafc')
fig.suptitle('ОПЕРАТИВНИЙ ОГЛЯД ОБСТАНОВКИ ІАЗ ОВУ (ТЕМА 5.3)', fontsize=15, fontweight='bold', color='#0f172a', y=0.97)

# Графік 1: Часові ряди атак (Варіант 2)
ax1 = plt.subplot(2, 2, 1)
days = ['Д-7', 'Д-6', 'Д-5', 'Д-4', 'Д-3', 'Д-2', 'Д-1']
ax1.plot(days, [25, 29, 34, 42, 38, 31, 27], marker='o', lw=2.5, color='#1e3a8a', label='Східний напрямок')
ax1.plot(days, [14, 18, 15, 22, 28, 19, 16], marker='s', lw=2.2, color='#4d7c0f', label='Північний напрямок')
ax1.plot(days, [10, 12, 11, 16, 19, 14, 12], marker='^', lw=2.0, color='#b45309', label='Південний напрямок')
ax1.set_title('1. Динаміка ворожих атак за напрямками (7 діб)', fontsize=11.5, fontweight='bold')
ax1.set_ylabel('Кількість атак')
ax1.set_ylim(0, 50)
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend()

# Графік 2: Структура сил противника (Варіант 3)
ax2 = plt.subplot(2, 2, 2)
labels = ['Піхота', 'Бронетехніка', 'Артилерія', 'БПЛА', 'РЕБ/ППО']
sizes = [38, 24, 18, 14, 6]
colors = ['#1e3a8a', '#4b5320', '#6b8e23', '#8b7355', '#64748b']
wedges, texts, autotexts = ax2.pie(
    sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
    pctdistance=0.75, wedgeprops=dict(width=0.48, edgecolor='white', lw=2)
)
for a in autotexts:
    a.set_color('white')
    a.set_fontweight('bold')
ax2.set_title('2. Структура виявлених сил противника (%)', fontsize=11.5, fontweight='bold')

# Графік 3: Кореляційна матриця втрат (Варіант 6)
ax3 = plt.subplot(2, 2, 3)
corr = np.array([
    [1.00,  0.78, -0.65,  0.42,  0.84],
    [0.78,  1.00, -0.52,  0.35,  0.71],
    [-0.65, -0.52, 1.00, -0.18, -0.61],
    [0.42,  0.35, -0.18,  1.00,  0.48],
    [0.84,  0.71, -0.61,  0.48,  1.00]
])
cols = ['Втрати прот.', 'Інтенс. атак', 'Відстань (км)', 'Погодні умови', 'Точність БПЛА']
sns.heatmap(corr, annot=True, fmt='.2f', cmap='YlGnBu', xticklabels=cols, yticklabels=cols, ax=ax3)
ax3.set_title('3. Кореляція факторів впливу на втрати противника', fontsize=11.5, fontweight='bold')
ax3.tick_params(axis='x', rotation=15)

# Графік 4: Сценарії прогнозування (Варіант 10)
ax4 = plt.subplot(2, 2, 4)
t_h, y_h = np.arange(1, 8), [25, 29, 34, 42, 38, 31, 27]
t_p = np.arange(7, 13)
y_b, y_pes, y_opt = [27, 26, 24, 25, 23, 22], [27, 32, 36, 39, 41, 44], [27, 22, 18, 15, 14, 12]
ax4.plot(t_h, y_h, marker='o', lw=2.5, color='#0f172a', label='Фактичні дані')
ax4.plot(t_p, y_b, marker='s', ls='--', lw=2, color='#1d4ed8', label='Базовий сценарій')
ax4.plot(t_p, y_pes, marker='^', ls=':', lw=2, color='#dc2626', label='Песимістичний')
ax4.plot(t_p, y_opt, marker='v', ls='-.', lw=2, color='#15803d', label='Оптимістичний')
ax4.fill_between(t_p, y_opt, y_pes, color='#94a3b8', alpha=0.25, label='Зона невизначеності')
ax4.axvline(x=7, color='#64748b', lw=1.2)
ax4.set_title('4. Прогнозування добової активності (+5 діб)', fontsize=11.5, fontweight='bold')
ax4.grid(True, linestyle='--', alpha=0.5)
ax4.legend(loc='upper left', fontsize=8.5)

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
png_path = os.path.join(BASE_DIR, "iaz_analytics_5_3.png")
plt.savefig(png_path, dpi=200)
plt.close()
print(f"✔ Графічний звіт збережено: {png_path}")

# ==============================================================================
# 2. ГЕНЕРАЦІЯ ІНТЕРАКТИВНОГО ДАШБОРДУ ОПЕРАТИВНОГО ОГЛЯДУ (ВАРІАНТ 7 + КАРТА)
# ==============================================================================
html_path = os.path.join(BASE_DIR, "operational_dashboard_5_3.html")

html_code = '''<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<title>Оперативний Дашборд ІАЗ ОВУ — Заняття 5.3</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  :root { --nato:#1e3a8a; --olive:#4b5320; --bg:#f1f5f9; --card:#ffffff; --txt:#0f172a; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:'Segoe UI',sans-serif; background:var(--bg); color:var(--txt); padding-bottom:40px; }
  header { background:linear-gradient(135deg,var(--nato),#2b4c7e); color:#fff; padding:16px 26px; display:flex; justify-content:space-between; align-items:center; }
  header h1 { margin:0; font-size:1.35rem; letter-spacing:0.3px; }
  .controls { display:flex; gap:10px; align-items:center; }
  select, button { padding:7px 12px; border-radius:5px; border:none; font-weight:600; cursor:pointer; }
  button { background:var(--olive); color:#fff; }
  main { max-width:1360px; margin:18px auto; padding:0 16px; }
  .kpi-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:18px; }
  .kpi { background:var(--card); padding:16px; border-radius:8px; border-left:5px solid var(--nato); box-shadow:0 2px 5px rgba(0,0,0,0.06); }
  .kpi small { color:#64748b; font-weight:700; text-transform:uppercase; font-size:0.75rem; }
  .kpi .val { font-size:1.8rem; font-weight:800; color:var(--nato); margin-top:4px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(410px,1fr)); gap:16px; margin-bottom:18px; }
  .panel { background:var(--card); padding:16px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.06); }
  .panel h2 { margin:0 0 12px; font-size:1rem; color:var(--nato); border-bottom:2px solid #e2e8f0; padding-bottom:6px; }
  #map { height:300px; border-radius:6px; }
  table { width:100%; border-collapse:collapse; font-size:0.88rem; }
  th, td { padding:9px; text-align:left; border-bottom:1px solid #e2e8f0; }
  th { background:#f8fafc; color:var(--nato); }
  .tag { padding:3px 8px; border-radius:4px; color:#fff; font-size:0.75rem; font-weight:700; }
</style>
</head>
<body>
<header>
  <h1>ОПЕРАТИВНИЙ ДАШБОРД ІАЗ ОВУ (ТЕМА 5.3 — КОМПЛЕКСНИЙ ОГЛЯД ОБСТАНОВКИ)</h1>
  <div class="controls">
    <label>Напрямок:</label>
    <select id="dirFilter" onchange="updateDashboard()">
      <option value="ALL">Усі напрямки</option>
      <option value="Східний">Східний напрямок</option>
      <option value="Північний">Північний напрямок</option>
      <option value="Південний">Південний напрямок</option>
    </select>
    <button onclick="window.print()">Друк звіту</button>
  </div>
</header>
<main>
  <div class="kpi-row">
    <div class="kpi"><small>Усього атак (7 діб)</small><div class="val" id="k-att">448</div></div>
    <div class="kpi" style="border-color:var(--olive)"><small>Переважаюче угруповання</small><div class="val" style="color:var(--olive)">Піхота (38%)</div></div>
    <div class="kpi" style="border-color:#b45309"><small>Пікова доба активності</small><div class="val" style="color:#b45309">Д-4 (80 атак)</div></div>
    <div class="kpi" style="border-color:#15803d"><small>Середня боєздатність ОУВ</small><div class="val" style="color:#15803d">85.4%</div></div>
  </div>

  <div class="grid">
    <div class="panel">
      <h2>1. Карта тактичної обстановки з нанесенням подій (Варіант 1 / 7)</h2>
      <div id="map"></div>
    </div>
    <div class="panel">
      <h2>2. Динаміка ворожих атак та прогноз (Варіанти 2 / 10)</h2>
      <canvas id="lineChart" height="145"></canvas>
    </div>
    <div class="panel">
      <h2>3. Структура сил противника (Варіант 3)</h2>
      <canvas id="pieChart" height="140"></canvas>
    </div>
    <div class="panel">
      <h2>4. Оцінка боєздатності підрозділів — Readiness (Варіант 4)</h2>
      <canvas id="radarChart" height="140"></canvas>
    </div>
  </div>

  <div class="panel">
    <h2>5. Журнал тактичних подій за координатами (Таблиця подій дашборду)</h2>
    <table>
      <thead><tr><th>Час</th><th>Напрямок</th><th>Координати</th><th>Тип події / Об'єкт</th><th>Інтенсивність</th><th>Статус</th></tr></thead>
      <tbody id="eventBody"></tbody>
    </table>
  </div>
</main>
<script>
const events = [
  { t:'06:40', d:'Східний', lat:48.72, lon:37.85, type:'Штурмові дії піхоти та ББМ', i:'Висока', c:'#dc2626' },
  { t:'08:15', d:'Східний', lat:48.58, lon:37.95, type:'Вогневий наліт артилерії', i:'Висока', c:'#dc2626' },
  { t:'10:30', d:'Північний', lat:49.85, lon:36.92, type:'Застосування ударних БПЛА', i:'Середня', c:'#d97706' },
  { t:'12:50', d:'Південний', lat:47.45, lon:35.85, type:'Переміщення резервів (колона)', i:'Низька', c:'#4b5320' },
  { t:'15:20', d:'Східний', lat:48.40, lon:37.80, type:'Робота комплексу РЕБ противника', i:'Середня', c:'#d97706' },
  { t:'17:45', d:'Північний', lat:49.65, lon:37.20, type:'Спроба інженерної розвідки', i:'Низька', c:'#4b5320' }
];

const map = L.map('map').setView([48.65, 36.90], 6);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution:'© OpenStreetMap' }).addTo(map);
let markersLayer = L.layerGroup().addTo(map);

const lineCtx = document.getElementById('lineChart').getContext('2d');
const lineChart = new Chart(lineCtx, {
  type: 'line',
  data: {
    labels: ['Д-7','Д-6','Д-5','Д-4','Д-3','Д-2','Д-1','П+1','П+2'],
    datasets: [
      { label:'Східний', data:[25,29,34,42,38,31,27,26,24], borderColor:'#1e3a8a', tension:0.2 },
      { label:'Північний', data:[14,18,15,22,28,19,16,15,14], borderColor:'#4b5320', tension:0.2 },
      { label:'Південний', data:[10,12,11,16,19,14,12,11,10], borderColor:'#b45309', tension:0.2 }
    ]
  }
});

new Chart(document.getElementById('pieChart'), {
  type: 'doughnut',
  data: {
    labels: ['Піхота (38%)','Бронетехніка (24%)','Артилерія (18%)','БПЛА (14%)','РЕБ/ППО (6%)'],
    datasets: [{ data:[38,24,18,14,6], backgroundColor:['#1e3a8a','#4b5320','#6b8e23','#8b7355','#64748b'] }]
  }
});

new Chart(document.getElementById('radarChart'), {
  type: 'radar',
  data: {
    labels: ['Особовий склад','Техніка','Забезпечення','Управління','МПС'],
    datasets: [
      { label:'1 МБр', data:[88,82,90,92,86], borderColor:'#1e3a8a', backgroundColor:'rgba(30,58,138,0.15)' },
      { label:'3 ДШБр', data:[92,70,68,88,90], borderColor:'#b45309', backgroundColor:'rgba(180,83,9,0.15)' }
    ]
  },
  options: { scales: { r: { min: 50, max: 100 } } }
});

function updateDashboard() {
  const dir = document.getElementById('dirFilter').value;
  markersLayer.clearLayers();
  const filtered = events.filter(e => dir === 'ALL' || e.d === dir);
  document.getElementById('eventBody').innerHTML = filtered.map(e => {
    L.circleMarker([e.lat, e.lon], { radius:9, fillColor:e.c, color:'#fff', weight:2, fillOpacity:0.9 })
      .bindPopup(`<b>${e.type}</b><br>Напрямок: ${e.d}<br>Час: ${e.t}<br>Інтенсивність: ${e.i}`).addTo(markersLayer);
    return `<tr><td><b>${e.t}</b></td><td>${e.d}</td><td>${e.lat}, ${e.lon}</td><td>${e.type}</td><td><span class="tag" style="background:${e.c}">${e.i}</span></td><td>Верифіковано ІАЗ</td></tr>`;
  }).join('');
}
updateDashboard();
</script>
</body>
</html>'''

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print(f"✔ Інтерактивний дашборд створено: {html_path}")
webbrowser.open(f"file:///{html_path}")