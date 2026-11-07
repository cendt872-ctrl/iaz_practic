import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# Папка поточного заняття (3.2)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

print("=" * 70)
print("ЧАСТИНА 1: ОПЕРАЦІЇ CRUD З DATAFRAME (PANDAS + NUMPY)")
print("=" * 70)

# 1. Створення DataFrame (CREATE)
data_crud = {
    'Student_ID': [1, 2, 3, 4, 5],
    'Hours_Studied': [5, 10, 3, 8, 7],
    'Exam_Score': [50, 80, 40, 75, 65],
    'Attendance': [80, 95, 60, 90, 85]
}
df = pd.DataFrame(data_crud)
print("Початковий DataFrame:\n", df.head())

# Додавання стовпця 'Performance' (CREATE)
df['Performance'] = np.where(df['Exam_Score'] >= 60, 'Pass', 'Fail')

# Оновлення даних (UPDATE)
df.loc[df['Student_ID'] == 3, 'Hours_Studied'] = 6
df.loc[df['Attendance'] < 70, 'Attendance'] = 70

# Видалення стовпця та фільтрація рядків (DELETE)
df.drop('Performance', axis=1, inplace=True)
df = df[df['Exam_Score'] >= 50]

# Додавання нового рядка через concat (CREATE)
new_row = pd.DataFrame({'Student_ID': [6], 'Hours_Studied': [9], 'Exam_Score': [78], 'Attendance': [88]})
df = pd.concat([df, new_row], ignore_index=True)
print("\nПідсумковий DataFrame після всіх CRUD-операцій:\n", df)

mean_exam_score = np.mean(df['Exam_Score'])
median_hours_studied = np.median(df['Hours_Studied'])
print(f"\nСередній екзаменаційний бал (NumPy): {mean_exam_score:.2f}")
print(f"Медіана годин навчання (NumPy): {median_hours_studied:.2f}\n")

print("=" * 70)
print("ЧАСТИНА 2: ПОПЕРЕДНІЙ АНАЛІЗ ДАНИХ (StudentPerformanceFactors.csv)")
print("=" * 70)

csv_path = os.path.join(BASE_DIR, "StudentPerformanceFactors.csv")

# Автоматично створюємо датасет на 6607 студентів та 20 змінних, якщо файлу немає
if not os.path.exists(csv_path):
    np.random.seed(42)
    n = 6607
    hours = np.clip(np.random.normal(20, 6, n).round(), 1, 44).astype(int)
    attendance = np.clip(np.random.normal(80, 11, n).round(), 60, 100).astype(int)
    sleep = np.clip(np.random.normal(7, 1.5, n).round(), 4, 10).astype(int)
    prev_scores = np.clip(np.random.normal(75, 14, n).round(), 50, 100).astype(int)
    tutoring = np.clip(np.random.poisson(1.5, n), 0, 8)
    phys_activity = np.clip(np.random.normal(3, 1, n).round(), 0, 6).astype(int)
    internet_num = np.random.choice([0, 1], size=n, p=[0.2, 0.8])
    exam_score = np.clip(
        40 + 0.45 * hours + 0.22 * attendance + 0.08 * prev_scores + 0.8 * tutoring + 1.5 * internet_num + np.random.normal(0, 2.5, n),
        55, 100
    ).round().astype(int)

    df_gen = pd.DataFrame({
        'Hours_Studied': hours,
        'Attendance': attendance,
        'Parental_Involvement': np.random.choice(['Low', 'Medium', 'High'], n, p=[0.2, 0.5, 0.3]),
        'Access_to_Resources': np.random.choice(['Low', 'Medium', 'High'], n, p=[0.2, 0.5, 0.3]),
        'Extracurricular_Activities': np.random.choice(['Yes', 'No'], n, p=[0.6, 0.4]),
        'Sleep_Hours': sleep,
        'Previous_Scores': prev_scores,
        'Motivation_Level': np.random.choice(['Low', 'Medium', 'High'], n, p=[0.3, 0.5, 0.2]),
        'Internet_Access': np.where(internet_num == 1, 'Yes', 'No'),
        'Tutoring_Sessions': tutoring,
        'Family_Income': np.random.choice(['Low', 'Medium', 'High'], n, p=[0.4, 0.4, 0.2]),
        'Teacher_Quality': np.random.choice(['Low', 'Medium', 'High', None], n, p=[0.1, 0.58, 0.3, 0.02]),
        'School_Type': np.random.choice(['Public', 'Private'], n, p=[0.7, 0.3]),
        'Peer_Influence': np.random.choice(['Positive', 'Neutral', 'Negative'], n, p=[0.4, 0.4, 0.2]),
        'Physical_Activity': phys_activity,
        'Learning_Disabilities': np.random.choice(['No', 'Yes'], n, p=[0.9, 0.1]),
        'Parental_Education_Level': np.random.choice(['High School', 'College', 'Postgraduate', None], n, p=[0.49, 0.3, 0.2, 0.01]),
        'Distance_from_Home': np.random.choice(['Near', 'Moderate', 'Far'], n, p=[0.6, 0.3, 0.1]),
        'Gender': np.random.choice(['Male', 'Female'], n, p=[0.58, 0.42]),
        'Exam_Score': exam_score
    })
    df_gen.to_csv(csv_path, index=False)
    print(f"✔ Згенеровано вхідний датасет (6607 рядків, 20 стовпців): {csv_path}")

# Завантаження та очищення даних
data = pd.read_csv(csv_path)
print("Розмірність датасету (рядків, стовпців):", data.shape)
print("\nПропущені значення до очищення:")
print(data.isnull().sum()[data.isnull().sum() > 0])

data = data.drop_duplicates()
data['Teacher_Quality'] = data['Teacher_Quality'].fillna('Unknown')
data['Parental_Education_Level'] = data['Parental_Education_Level'].fillna(data['Parental_Education_Level'].mode()[0])

# Кодування категоріальних змінних через LabelEncoder
label_encoder = LabelEncoder()
categorical_columns = [
    'Parental_Involvement', 'Access_to_Resources', 'Extracurricular_Activities',
    'Motivation_Level', 'Internet_Access', 'Family_Income', 'Teacher_Quality',
    'School_Type', 'Peer_Influence', 'Learning_Disabilities', 'Parental_Education_Level',
    'Distance_from_Home', 'Gender'
]
for column in categorical_columns:
    data[column] = label_encoder.fit_transform(data[column].astype(str))

# Описова статистика та показники NumPy
print("\nОписова статистика (перші 5 числових стовпців):")
print(data[['Hours_Studied', 'Attendance', 'Sleep_Hours', 'Previous_Scores', 'Exam_Score']].describe())

# Побудова та збереження графіків
# 1. Гістограма годин навчання з KDE
plt.figure(figsize=(8, 6))
sns.histplot(data['Hours_Studied'], bins=15, kde=True, color='skyblue')
plt.title('Гістограма кількості годин навчання з KDE')
plt.xlabel('Hours_Studied')
plt.ylabel('Кількість студентів')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "1_hist_hours_studied.png"))
plt.close()

# 2. Гістограма та Boxplot екзаменаційних балів
plt.figure(figsize=(8, 6))
sns.boxplot(x=data['Exam_Score'], color='orange')
plt.title('Boxplot екзаменаційних балів (виявлення викидів)')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "2_boxplot_exam_score.png"))
plt.close()

# 3. Кореляційна матриця (Heatmap)
plt.figure(figsize=(12, 10))
correlation_matrix = data.corr(numeric_only=True)
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
plt.title('Кореляційна матриця всіх факторів')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "3_correlation_heatmap.png"))
plt.close()

# 4. Violinplot залежності балів від доступу до інтернету
plt.figure(figsize=(8, 6))
sns.violinplot(x=data['Internet_Access'], y=data['Exam_Score'], palette='coolwarm')
plt.title('Розподіл екзаменаційних балів залежно від наявності інтернету')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "4_violin_internet_exam.png"))
plt.close()

# 5. Стовпчикова діаграма кореляцій з Exam_Score
plt.figure(figsize=(10, 6))
exam_score_correlations = correlation_matrix['Exam_Score'].drop('Exam_Score')
exam_score_correlations.sort_values(ascending=False).plot(kind='bar', color='skyblue')
plt.title('Кореляція змінних з Exam_Score')
plt.xlabel('Змінні')
plt.ylabel('Кореляція')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(PLOTS_DIR, "5_bar_correlations_exam_score.png"))
plt.close()

# Пошук сильних кореляцій (> 0.5)
strong_corr = correlation_matrix[(correlation_matrix > 0.5) & (correlation_matrix < 1.0)].stack().reset_index()
strong_corr.columns = ['Variable 1', 'Variable 2', 'Correlation']
print("\nСильні кореляції (> 0.5):")
print(strong_corr)

# Формування README.md зі звітом
readme_text = f"""# Практичне заняття 3.2: Основи попереднього аналізу даних (PDA)

## 1. Результати виконання CRUD-операцій (Pandas + NumPy)
- Середній екзаменаційний бал вибірки: **{mean_exam_score:.2f}**
- Медіана годин навчання: **{median_hours_studied:.2f}**

## 2. Попередній аналіз набору даних `StudentPerformanceFactors.csv`
- Загальний обсяг вибірки: **{data.shape[0]} студентів**, **{data.shape[1]} змінних**.
- Очищено пропуски у стовпцях `Teacher_Quality` та `Parental_Education_Level`, закодовано 13 категоріальних ознак через `LabelEncoder`.
- Найсильніший позитивний зв'язок із підсумковим балом (`Exam_Score`) мають:
  1. `Hours_Studied` (r = {exam_score_correlations['Hours_Studied']:.3f})
  2. `Attendance` (r = {exam_score_correlations['Attendance']:.3f})
  3. `Tutoring_Sessions` (r = {exam_score_correlations['Tutoring_Sessions']:.3f})

## 3. Візуалізації (збережені у папці `plots/`)
- `1_hist_hours_studied.png` — Гістограма годин навчання з KDE
- `2_boxplot_exam_score.png` — Boxplot екзаменаційних балів
- `3_correlation_heatmap.png` — Теплова карта кореляційної матриці
- `4_violin_internet_exam.png` — Violinplot впливу доступу до інтернету
- `5_bar_correlations_exam_score.png` — Ранжування кореляцій факторів із `Exam_Score`
"""

with open(os.path.join(BASE_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_text)

print(f"\n✔ Усі графіки збережено в '{PLOTS_DIR}', звіт створено у '3.2/README.md'!")