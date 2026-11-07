import os
import pandas as pd
from datetime import datetime, timedelta

INPUT_FILE = "input_data.xlsx"
OUTPUT_FILE = "filtered_data.xlsx"

# Крок 1. Створюємо демонстраційний вихідний Excel-файл, якщо його ще не існує
if not os.path.exists(INPUT_FILE):
    sample_data = {
        "Підрозділ": ["1 МБ", "2 МБ", "ТБ", "ББпС", "ЗРДн", "РВБ"],
        "Ресурс": ["Бocприпаси (ум. од.)", "ПММ (тонн)", "Запчастини (компл.)", "БпЛА (од.)", "Ракети ППО", "Ремкомплекти"],
        "Кількість": [45, 12, 28, 35, 8, 22],
        "Дата_звіту": [
            (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"), # Старий запис (> місяця)
            (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"), # Старий запис (> місяця)
            (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        ]
    }
    df_init = pd.DataFrame(sample_data)
    df_init.to_excel(INPUT_FILE, index=False)
    print(f"✔ Створено вхідну таблицю Excel: {INPUT_FILE}")

# Крок 2. Читаємо дані з Excel-файлу за допомогою pandas
df = pd.read_excel(INPUT_FILE)
df["Дата_звіту"] = pd.to_datetime(df["Дата_звіту"])

# Крок 3. Фільтруємо дані:
# Умова А (базова): записи за останні 30 днів (останній місяць)
one_month_ago = datetime.now() - timedelta(days=30)
# Умова Б (Варіант 2): числове значення 'Кількість' більше ніж 15
filtered_df = df[(df["Дата_звіту"] >= one_month_ago) & (df["Кількість"] > 15)].copy()

# Форматуємо дату назад у зручний вигляд для збереження
filtered_df["Дата_звіту"] = filtered_df["Дата_звіту"].dt.strftime("%Y-%m-%d")

# Крок 4. Зберігаємо відфільтровані дані у новий Excel-файл
filtered_df.to_excel(OUTPUT_FILE, index=False)
print(f"✔ Відфільтровано записів: {len(filtered_df)} із {len(df)}.")
print(f"✔ Результат збережено у файл: {OUTPUT_FILE}")
print("\nВідфільтрована таблиця:")
print(filtered_df)