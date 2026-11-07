import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 1. Шляхи та папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "deployment_environments.csv")

if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "deployment_environments.csv")

print(f"Завантаження даних із: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# 2. Очищення та трансформація
df.drop_duplicates(inplace=True)
scaler = MinMaxScaler()
df['vram_scaled'] = scaler.fit_transform(df[['vram_gb']])

le_gpu = LabelEncoder()
df['gpu_encoded'] = le_gpu.fit_transform(df['gpu'])
le_loc = LabelEncoder()
df['location_encoded'] = le_loc.fit_transform(df['location'])

df_transformed = pd.get_dummies(df, columns=['location'], prefix='loc')

# 3. Декомпозиція та Машинне Навчання (Лінійна регресія)
train_set, test_set = train_test_split(df_transformed, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(train_set[['gpu_encoded', 'location_encoded']], train_set['vram_gb'])
predictions = model.predict(test_set[['gpu_encoded', 'location_encoded']])

mse = mean_squared_error(test_set['vram_gb'], predictions)
r2 = r2_score(test_set['vram_gb'], predictions)

# Підготовка даних для генерації HTML-елементів
deployments = df['deployment'].tolist()
vram_values = df['vram_gb'].tolist()
max_vram = max(vram_values)

avg_vram_by_loc = df.groupby('location')['vram_gb'].mean().to_dict()

# Генерація HTML рядків для анімованих смуг (барчарт)
bars_html = ""
for dep, vram in zip(deployments, vram_values):
    pct = int((vram / max_vram) * 100)
    bars_html += f"""
    <div class="bar-row">
        <span class="bar-label">{dep} ({vram} GB)</span>
        <div class="bar-track">
            <div class="bar-fill" style="width: 0%;" data-width="{pct}%"></div>
        </div>
    </div>
    """

# Генерація кругових прогрес-барів для локацій
loc_html = ""
colors = ['#38bdf8', '#34d399', '#fbbf24', '#f43f5e']
for i, (loc, avg_val) in enumerate(avg_vram_by_loc.items()):
    col = colors[i % len(colors)]
    loc_html += f"""
    <div class="loc-item">
        <div class="loc-title">{loc}</div>
        <div class="loc-value" style="color: {col};">Сер. VRAM: {avg_val:.1f} GB</div>
        <div class="progress-track">
            <div class="progress-fill" style="width: 0%; background: {col};" data-width="{int((avg_val/80)*100)}%"></div>
        </div>
    </div>
    """

# 4. Створення автономного анімованого HTML-дашборду
html_content = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналітичний дашборд: Середовища розгортання ШІ (Практика 3.5)</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 25px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #1e293b, #334155);
            border: 1px solid #475569;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }}
        header h1 {{
            margin: 0;
            color: #38bdf8;
            font-size: 26px;
        }}
        header p {{
            color: #94a3b8;
            margin-top: 8px;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background: #1e293b;
            border: 1px solid #334155;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card h3 {{
            margin: 0;
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .card p {{
            margin: 12px 0 0 0;
            font-size: 28px;
            font-weight: bold;
            color: #38bdf8;
        }}
        .section {{
            background: #1e293b;
            border: 1px solid #334155;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            margin-bottom: 25px;
        }}
        .section h2 {{
            border-bottom: 1px solid #334155;
            padding-bottom: 12px;
            color: #38bdf8;
            margin-top: 0;
            font-size: 18px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }}
        .chart-box {{
            background: #0f172a;
            border: 1px solid #334155;
            padding: 20px;
            border-radius: 10px;
        }}
        .chart-box h3 {{
            margin-top: 0;
            color: #cbd5e1;
            font-size: 15px;
            text-align: center;
            margin-bottom: 20px;
        }}
        /* Анімовані смугові графіки */
        .bar-row {{
            margin-bottom: 12px;
        }}
        .bar-label {{
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 4px;
            display: block;
        }}
        .bar-track {{
            background: #1e293b;
            border-radius: 6px;
            height: 18px;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            border-radius: 4px;
            transition: width 1.5s cubic-bezier(0.1, 0.9, 0.2, 1);
        }}
        /* Анімовані прогрес-бари локацій */
        .loc-item {{
            margin-bottom: 20px;
        }}
        .loc-title {{
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }}
        .loc-value {{
            font-size: 13px;
            margin-bottom: 6px;
        }}
        .progress-track {{
            background: #1e293b;
            border-radius: 6px;
            height: 14px;
            overflow: hidden;
            border: 1px solid #334155;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 1.8s cubic-bezier(0.1, 0.9, 0.2, 1);
        }}
        .metrics-box {{
            background: #0f172a;
            border: 1px solid #334155;
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
            color: #34d399;
        }}
        ul {{
            line-height: 1.7;
            color: #cbd5e1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Аналітичний дашборд: Середовища розгортання ШІ</h1>
            <p>Практична робота 3.5: Очищення, трансформація, декомпозиція та регресійне моделювання</p>
        </header>

        <div class="cards-grid">
            <div class="card">
                <h3>Всього середовищ</h3>
                <p>{len(df)}</p>
            </div>
            <div class="card">
                <h3>Максимальна VRAM</h3>
                <p>{df['vram_gb'].max()} GB</p>
            </div>
            <div class="card">
                <h3>Середня VRAM</h3>
                <p>{df['vram_gb'].mean():.1f} GB</p>
            </div>
            <div class="card">
                <h3>Якість моделі (R² Score)</h3>
                <p>{r2:.2f}</p>
            </div>
        </div>

        <div class="section">
            <h2>Інтерактивні анімовані візуалізації</h2>
            <div class="charts-grid">
                <div class="chart-box">
                    <h3>Розподіл VRAM по середовищах розгортання</h3>
                    {bars_html}
                </div>
                <div class="chart-box">
                    <h3>Середній об'єм VRAM за типами локацій</h3>
                    {loc_html}
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Результати машинного навчання (Лінійна регресія)</h2>
            <p>Модель навчена на підставі параметрів GPU та локації для прогнозування об'єму пам'яті (`vram_gb`).</p>
            <div class="metrics-box">
                > Розмір тесту: {len(test_set)} зразків<br>
                > Середньоквадратична похибка (MSE): {mse:.4f}<br>
                > Коефіцієнт детермінації (R²): {r2:.4f}
            </div>
        </div>

        <div class="section">
            <h2>Аналітичні висновки</h2>
            <ul>
                <li><strong>Трансформація даних:</strong> Успішно виконано нормалізацію числових показників за допомогою MinMaxScaler та кодування категоріальних змінних.</li>
                <li><strong>Розподіл ресурсів:</strong> Найбільші об'єми відеопам'яті (до 80 GB) зосереджені в датацентрах та хмарних кластерах корпоративного рівня (A100/H100).</li>
                <li><strong>Предиктивна здатність:</strong> Побудована модель лінійної регресії демонструє стабільність завдяки чіткій кореляції між класом обладнання та архітектурною локацією.</li>
            </ul>
        </div>
    </div>

    <script>
        // Запуск плавних CSS-анімацій при завантаженні сторінки
        window.addEventListener('DOMContentLoaded', () => {{
            setTimeout(() => {{
                document.querySelectorAll('.bar-fill, .progress-fill').forEach(el => {{
                    el.style.width = el.getAttribute('data-width');
                }});
            }}, 300);
        }});
    </script>
</body>
</html>
"""

dashboard_path = os.path.join(BASE_DIR, "dashboard.html")
with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✔ Дашборд успішно згенеровано! Відкрийте файл у браузері: {dashboard_path}")