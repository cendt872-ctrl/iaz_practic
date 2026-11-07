import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 1. Шляхи та папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
data_path = os.path.join(BASE_DIR, 'deployment_environments.csv')

print("=== 1. ЗАВАНТАЖЕННЯ ДАНИХ ===")
df = pd.read_csv(data_path)
print(df.head())

print("\n=== 2. ОЧИЩЕННЯ ДАНИХ ===")
df.drop_duplicates(inplace=True)
df['gpu_code'] = df['gpu'].astype('category').cat.codes
df['location_code'] = df['location'].astype('category').cat.codes

print("\n=== 3. ТРАНСФОРМАЦІЯ ДАНИХ ===")
scaler = MinMaxScaler()
df['vram_scaled'] = scaler.fit_transform(df[['vram_gb']])
df_transformed = pd.get_dummies(df, columns=['location'], prefix='loc')

print("\n=== 4. ДЕКОМПОЗИЦІЯ ТА КОРЕЛЯЦІЙНИЙ АНАЛІЗ ===")
train_set, test_set = train_test_split(df_transformed, test_size=0.2, random_state=42)
print(f"Train size: {len(train_set)} | Test size: {len(test_set)}")

correlation_matrix = df[['vram_gb', 'gpu_code', 'location_code', 'vram_scaled']].corr()
print("\nКореляційна матриця:")
print(correlation_matrix)

print("\n=== 5. ОПИСОВА СТАТИСТИКА ===")
print(df.describe())

print("\n=== 6. ПОБУДОВА МОДЕЛІ МАШИННОГО НАВЧАННЯ ===")
model = LinearRegression()
features = ['gpu_code', 'location_code']
target = 'vram_gb'
model.fit(train_set[features], train_set[target])
predictions = model.predict(test_set[features])

print("Прогноз VRAM:", predictions.round(1))
print("Фактичний VRAM:", test_set[target].values)
print(f"MSE: {mean_squared_error(test_set[target], predictions):.4f}")
print(f"R2 Score: {r2_score(test_set[target], predictions):.4f}")

print("\n=== 7. ГЕНЕРАЦІЯ ТА ЗБЕРЕЖЕННЯ ГРАФІКІВ ===")
# Графік 1: Гістограма розподілу VRAM
plt.figure(figsize=(8, 5))
sns.histplot(df['vram_gb'], bins=6, kde=True, color='skyblue')
plt.title('Розподіл об\'єму VRAM (Гістограма)')
plt.xlabel('VRAM (GB)')
plt.ylabel('Частота')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "vram_distribution.png"), dpi=150)
plt.close()

# Графік 2: Boxplot для виявлення викидів
plt.figure(figsize=(8, 4))
sns.boxplot(x=df['vram_gb'], color='orange')
plt.title('Коробкова діаграма (Boxplot) для VRAM')
plt.xlabel('VRAM (GB)')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "vram_boxplot.png"), dpi=150)
plt.close()

# Графік 3: Теплова карта кореляцій
plt.figure(figsize=(7, 6))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
plt.title('Кореляційна матриця ознак')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "correlation_heatmap.png"), dpi=150)
plt.close()

print(f"✔ Усі графіки успішно збережено у папку: {PLOTS_DIR}")