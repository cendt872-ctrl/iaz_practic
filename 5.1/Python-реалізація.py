import os
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Визначаємо папку, де лежить сам скрипт (5.1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Створення DataFrame з навчальними даними ІАЗ ОВУ
data = {
    'Ділянка': ['Ділянка A', 'Ділянка B', 'Ділянка C', 'Ділянка D', 'Ділянка E'],
    'Чисельність': [12, 19, 7, 15, 9],
    'Статус': ['Контролюється', 'Висока активність', 'Стабільно', 'Активність', 'Контролюється']
}
df = pd.DataFrame(data)

print("=== Зведена статистика по ділянках ===")
print(df)

# 2. Збереження інтерактивного графіку Plotly (відкривається у браузері)
fig = px.bar(
    df, 
    x='Ділянка', 
    y='Чисельність', 
    color='Статус',
    title='Оперативна чисельність виявлених об’єктів за секторами (Інтерактивний)',
    labels={'Чисельність': 'Кількість об’єктів', 'Ділянка': 'Ділянка місцевості'}
)
fig.update_layout(template='plotly_white')

html_path = os.path.join(BASE_DIR, "interactive_chart.html")
fig.write_html(html_path)
print(f"\n✔ Інтерактивний графік збережено: {html_path}")

# Розкоментуйте наступний рядок, якщо хочете, щоб браузер відкривався автоматично при запуску:
# fig.show()

# 3. Збереження статичної картинки PNG (для звіту Word)
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8, 5))
ax = sns.barplot(x='Ділянка', y='Чисельність', data=df, hue='Ділянка', palette='Blues_d', legend=False)

for p in ax.patches:
    ax.annotate(f"{int(p.get_height())}", 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 8), 
                textcoords='offset points',
                fontsize=11, fontweight='bold')

plt.title('Чисельність виявлених об’єктів на ділянках місцевості', fontsize=12, fontweight='bold', pad=15)
plt.xlabel('Ділянка місцевості', fontsize=10)
plt.ylabel('Кількість об’єктів', fontsize=10)
plt.ylim(0, 22)

png_path = os.path.join(BASE_DIR, "objects_distribution.png")
plt.tight_layout()
plt.savefig(png_path, dpi=200)
plt.close()
print(f"✔ Графік-картинку збережено: {png_path}")