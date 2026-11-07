# Практичне заняття 3.2: Основи попереднього аналізу даних (PDA)

## 1. Результати виконання CRUD-операцій (Pandas + NumPy)
- Середній екзаменаційний бал вибірки: **69.60**
- Медіана годин навчання: **8.00**

## 2. Попередній аналіз набору даних `StudentPerformanceFactors.csv`
- Загальний обсяг вибірки: **6607 студентів**, **20 змінних**.
- Очищено пропуски у стовпцях `Teacher_Quality` та `Parental_Education_Level`, закодовано 13 категоріальних ознак через `LabelEncoder`.
- Найсильніший позитивний зв'язок із підсумковим балом (`Exam_Score`) мають:
  1. `Hours_Studied` (r = 0.586)
  2. `Attendance` (r = 0.479)
  3. `Tutoring_Sessions` (r = 0.224)

## 3. Візуалізації (збережені у папці `plots/`)
- `1_hist_hours_studied.png` — Гістограма годин навчання з KDE
- `2_boxplot_exam_score.png` — Boxplot екзаменаційних балів
- `3_correlation_heatmap.png` — Теплова карта кореляційної матриці
- `4_violin_internet_exam.png` — Violinplot впливу доступу до інтернету
- `5_bar_correlations_exam_score.png` — Ранжування кореляцій факторів із `Exam_Score`
