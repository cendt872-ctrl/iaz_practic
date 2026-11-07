import sqlite3
import pandas as pd

# Створюємо підключення до реляційної бази даних (файл iaz_database.db створиться автоматично)
conn = sqlite3.connect("iaz_database.db")
cursor = conn.cursor()

# Очищаємо таблиці, якщо скрипт запускається повторно
cursor.execute("DROP TABLE IF EXISTS Personnel;")
cursor.execute("DROP TABLE IF EXISTS Units;")

# 1. СТВОРЕННЯ ТАБЛИЦЬ (CREATE TABLE)
# Створюємо таблицю Units (для прикладу №7 з JOIN) та таблицю Personnel
cursor.execute("""
CREATE TABLE Units (
    Unit_ID VARCHAR(50) PRIMARY KEY,
    Unit_Name VARCHAR(100)
);
""")

cursor.execute("""
CREATE TABLE Personnel (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Unit VARCHAR(100),
    Date_Joined DATE
);
""")
print("✔ 1. Таблиці Personnel та Units успішно створено.")

# 2. ВСТАВКА ДАНИХ (INSERT INTO)
cursor.executemany("INSERT INTO Units VALUES (?, ?);", [
    ("Engineering", "Інженерно-саперний батальйон"),
    ("AirDefense", "Дивізіон ППО"),
    ("Logistics", "Батальйон логістики")
])

cursor.executemany("""
INSERT INTO Personnel (Name, Rank, Unit, Date_Joined)
VALUES (?, ?, ?, ?);
""", [
    ("John Doe", "Captain", "Engineering", "2020-05-01"),
    ("Олександр Коваль", "Lieutenant", "Engineering", "2022-03-15"),
    ("Іван Петренко", "Sergeant", "AirDefense", "2021-08-10"),
    ("Максим Бондар", "Major", "Logistics", "2023-11-20")
])
conn.commit()
print("✔ 2. Дані успішно додано в таблиці.\n")

# 3. ОТРИМАННЯ ДАНИХ (SELECT)
print("--- 3. Військовослужбовці підрозділу 'Engineering': ---")
df_select = pd.read_sql_query("SELECT Name, Rank FROM Personnel WHERE Unit = 'Engineering';", conn)
print(df_select, "\n")

# 4. ОНОВЛЕННЯ ДАНИХ (UPDATE)
cursor.execute("UPDATE Personnel SET Rank = 'Major' WHERE ID = 1;")
conn.commit()
print("✔ 4. Звання для ID = 1 оновлено на 'Major'.\n")

# 6. АГРЕГАТНІ ФУНКЦІЇ (COUNT)
print("--- 6. Загальна кількість військовослужбовців: ---")
df_count = pd.read_sql_query("SELECT COUNT(*) AS Total FROM Personnel;", conn)
print(df_count, "\n")

# 7. ОБ'ЄДНАННЯ ТАБЛИЦЬ (JOIN)
print("--- 7. Об'єднання таблиць Personnel та Units (JOIN): ---")
df_join = pd.read_sql_query("""
SELECT Personnel.Name, Personnel.Rank, Units.Unit_Name
FROM Personnel
JOIN Units ON Personnel.Unit = Units.Unit_ID;
""", conn)
print(df_join, "\n")

# 8. ГРУПУВАННЯ ДАНИХ (GROUP BY)
print("--- 8. Кількість особового складу за підрозділами (GROUP BY): ---")
df_group = pd.read_sql_query("""
SELECT Unit, COUNT(*) as Total_Personnel
FROM Personnel
GROUP BY Unit;
""", conn)
print(df_group, "\n")

# 9. СОРТУВАННЯ ДАНИХ (ORDER BY)
print("--- 9. Сортування за датою вступу на службу (від найновіших): ---")
df_order = pd.read_sql_query("""
SELECT Name, Rank, Date_Joined
FROM Personnel
ORDER BY Date_Joined DESC;
""", conn)
print(df_order, "\n")

# 10. ВИКОРИСТАННЯ ПІДЗАПИТІВ (Subquery)
print("--- 10. Хто приєднався до підрозділу найпізніше: ---")
df_sub = pd.read_sql_query("""
SELECT Name, Date_Joined
FROM Personnel
WHERE Date_Joined = (SELECT MAX(Date_Joined) FROM Personnel);
""", conn)
print(df_sub, "\n")

# 5. ВИДАЛЕННЯ ДАНИХ (DELETE)
cursor.execute("DELETE FROM Personnel WHERE Rank = 'Captain';")
conn.commit()
print("✔ 5. Записи зі званням 'Captain' видалено (якщо такі залишалися).")

conn.close()