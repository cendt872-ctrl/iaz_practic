import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Шляхи та папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# 2. Завантаження даних
csv_path = os.path.join(BASE_DIR, "russia_losses_equipment.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join(os.path.dirname(BASE_DIR), "russia_losses_equipment.csv")

print(f"Завантаження даних із: {csv_path}")
df = pd.read_csv(csv_path)

# 3. Очищення даних
df.drop_duplicates(inplace=True)
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

# 4. Розрахунок статистики для дашборду
total_days = len(df)
max_tanks = int(df['tank'].max())
max_apc = int(df['APC'].max())
max_artillery = int(df['field artillery'].max())
max_drones = int(df['drone'].max())

mean_tanks = float(df['tank'].mean())
mean_apc = float(df['APC'].mean())

# 5. Побудова графіків
# Графік 1: Гістограма втрат танків
plt.figure(figsize=(8, 4))
sns.histplot(df['tank'], bins=25, kde=True, color='firebrick')
plt.title('Розподіл сумарних втрат танків')
plt.xlabel('Кількість одиниць')
plt.ylabel('Частота (днів)')
plt.tight_layout()
chart1_path = os.path.join(PLOTS_DIR, "tank_hist.png")
plt.savefig(chart1_path, dpi=120)
plt.close()

# Графік 2: Boxplot
plt.figure(figsize=(8, 4))
sns.boxplot(data=df[['tank', 'APC', 'field artillery', 'drone']], palette='Set2')
plt.title('Розмах та викиди по основній техніці')
plt.ylabel('Кількість')
plt.tight_layout()
chart2_path = os.path.join(PLOTS_DIR, "equipment_box.png")
plt.savefig(chart2_path, dpi=120)
plt.close()

# Графік 3: Динаміка часового ряду
if 'date' in df.columns:
    plt.figure(figsize=(10, 4))
    plt.plot(df['date'], df['tank'], color='darkred', linewidth=2)
    plt.title('Динаміка накопичення втрат танків у часі')
    plt.xlabel('Дата')
    plt.ylabel('Загальна кількість')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    chart3_path = os.path.join(PLOTS_DIR, "tank_timeline.png")
    plt.savefig(chart3_path, dpi=120)
    plt.close()

# Графік 4: Теплова карта кореляцій
key_equip = ['tank', 'APC', 'field artillery', 'MRL', 'drone', 'anti-aircraft warfare']
corr_matrix = df[key_equip].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
plt.title('Матриця кореляцій')
plt.tight_layout()
chart4_path = os.path.join(PLOTS_DIR, "correlation_heatmap.png")
plt.savefig(chart4_path, dpi=120)
plt.close()

# 6. Генерація автономного HTML-дашборду (dashboard.html)
html_content = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналітичний дашборд: Втрати техніки</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f6f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
            border-left: 5px solid #2a5298;
        }}
        .card h3 {{
            margin: 0;
            font-size: 14px;
            color: #777;
            text-transform: uppercase;
        }}
        .card p {{
            margin: 10px 0 0 0;
            font-size: 24px;
            font-weight: bold;
            color: #1e3c72;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 25px;
        }}
        .section h2 {{
            border-bottom: 2px solid #eaeaea;
            padding-bottom: 10px;
            color: #1e3c72;
            margin-top: 0;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            justify-items: center;
        }}
        .chart-box {{
            background: #fafafa;
            border: 1px solid #e1e4e8;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }}
        .chart-box img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        ul {{
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Аналітичний дашборд: Втрати техніки</h1>
            <p>Практична робота: Попередній аналіз даних (PDA) та візуалізація часових рядів</p>
        </header>

        <div class="cards-grid">
            <div class="card">
                <h3>Всього днів спостереження</h3>
                <p>{total_days}</p>
            </div>
            <div class="card">
                <h3>Максимум втрат танків</h3>
                <p>{max_tanks}</p>
            </div>
            <div class="card">
                <h3>Максимум втрат ББМ (APC)</h3>
                <p>{max_apc}</p>
            </div>
            <div class="card">
                <h3>Максимум арт. систем</h3>
                <p>{max_artillery}</p>
            </div>
        </div>

        <div class="section">
            <h2>Візуалізація та розподіл даних</h2>
            <div class="charts-grid">
                <div class="chart-box">
                    <h3>Гістограма втрат танків</h3>
                    <img src="plots/tank_hist.png" alt="Гістограма танків">
                </div>
                <div class="chart-box">
                    <h3>Коробкова діаграма (Boxplot)</h3>
                    <img src="plots/equipment_box.png" alt="Boxplot">
                </div>
                <div class="chart-box">
                    <h3>Динаміка накопичення (Timeline)</h3>
                    <img src="plots/tank_timeline.png" alt="Timeline">
                </div>
                <div class="chart-box">
                    <h3>Кореляційна матриця (Heatmap)</h3>
                    <img src="plots/correlation_heatmap.png" alt="Heatmap">
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Аналітичні висновки</h2>
            <ul>
                <li><strong>Очищення та структура:</strong> Набір даних містить {total_days} записів. Пропущені значення в числових показниках успішно оброблено.</li>
                <li><strong>Динаміка показників:</strong> Графік часового ряду демонструє неперервний кумулятивний характер зростання загальних втрат (зокрема танків до рівня {max_tanks} од.).</li>
                <li><strong>Взаємозв'язки:</strong> Кореляційний аналіз підтверджує наявність сильного лінійного зв'язку між накопиченням різних видів важкої техніки (коефіцієнти кореляції близькі до 1.0), що зумовлено специфікою звітності на основі часових рядів.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

dashboard_path = os.path.join(BASE_DIR, "dashboard.html")
with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✔ Дашборд успішно згенеровано! Відкрийте файл у браузері: {dashboard_path}")