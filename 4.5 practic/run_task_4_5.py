import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# 1. Шляхи та папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)
data_path = os.path.join(BASE_DIR, 'heart.csv')

if not os.path.exists(data_path):
    data_path = os.path.join(os.path.dirname(BASE_DIR), 'heart.csv')

print("=== 1. ЗАВАНТАЖЕННЯ ДАНИХ ===")
df = pd.read_csv(data_path)
df.drop_duplicates(inplace=True)

# 2. Розподіл даних (80:20)
X = df.drop("target", axis=1).select_dtypes(include=["number"])
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Навчання моделей
models = {
    "Логістична регресія": LogisticRegression(max_iter=1000),
    "Метод сусідів (KNN)": KNeighborsClassifier(),
    "Випадковий ліс (RF)": RandomForestClassifier(random_state=42),
    "Опорні вектори (SVM)": SVC(probability=True, random_state=42)
}

model_names = []
accuracies = []

print("\n=== 4. ОЦІНКА ТОЧНОСТІ МОДЕЛЕЙ ===")
for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds) * 100  # у відсотках для наочності
    
    model_names.append(name)
    accuracies.append(acc)
    print(f"Точність моделі '{name}': {acc:.1f}%")

# 5. Створення наочної візуалізації для командира (Порівняння моделей)
plt.figure(figsize=(9, 5))
bars = plt.barh(model_names, accuracies, color=['#2563eb', '#38bdf8', '#22c55e', '#f59e0b'])
plt.xlabel('Точність прогнозування (%)', fontsize=12, fontweight='bold')
plt.title('Порівняння ефективності алгоритмів діагностики', fontsize=14, fontweight='bold', pad=15)
plt.xlim(0, 100)

# Додаємо значення на графік
for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
             va='center', ha='left', fontsize=11, fontweight='bold')

plt.gca().invert_yaxis()  # Найкраща модель зверху
plt.grid(axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "commander_model_comparison.png"), dpi=200)
plt.close()

# 6. Зрозуміла матриця результатів для найкращої моделі (Випадковий ліс)
best_model = models["Випадковий ліс (RF)"]
y_pred = best_model.predict(X_test)
conf_matrix = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(7, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Greens', cbar=False, 
            annot_kws={"size": 16, "weight": "bold"})
plt.title('Аналіз результатів перевірки (Матриця рішень)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Прогноз системи (0 - Здоровий, 1 - Ризик)', fontsize=11)
plt.ylabel('Фактичний стан пацієнта', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "commander_decision_matrix.png"), dpi=200)
plt.close()

print(f"\n✔ Зрозумілі візуалізації для командира успішно згенеровано у папці: {PLOTS_DIR}")