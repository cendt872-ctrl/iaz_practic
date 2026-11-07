# Технічна документація бази даних ІАЗ ОУВ (Заняття 2.5)

## 1. Архітектура бази даних та опис варіантів
База даних `iaz_all_17_variants.db` (та серверна версія у PostgreSQL) містить 34 взаємопов'язані таблиці для всіх 17 варіантів:

| Варіант | Таблиця 1 (Персонал / Штаб) | Таблиця 2 (Підрозділи / Завдання / Об'єкти) | Ключ зв'язку (Foreign Key) |
| :--- | :--- | :--- | :--- |
| Варіант 1 (`variant_01_officers_units.xlsx`) | `Officers` | `Units` | `Unit_ID` |
| Варіант 2 (`variant_02_logistics.xlsx`) | `Logistics_Personnel` | `Logistics_Units` | `Logistics_Unit_ID` |
| Варіант 3 (`variant_03_operations.xlsx`) | `Operations_Staff` | `Operations` | `Operation_ID` |
| Варіант 4 (`variant_04_equipment.xlsx`) | `Equipment_Personnel` | `Equipment` | `Equipment_ID` |
| Варіант 5 (`variant_05_weapons.xlsx`) | `Weapons_Personnel` | `Weapons` | `Weapon_ID` |
| Варіант 6 (`variant_06_training.xlsx`) | `Training_Personnel` | `Training_Programs` | `Training_Program_ID` |
| Варіант 7 (`variant_07_intelligence.xlsx`) | `Intelligence_Personnel` | `Intelligence_Tasks` | `Task_ID` |
| Варіант 8 (`variant_08_medical.xlsx`) | `Medical_Staff` | `Medical_Units` | `Medical_Unit_ID` |
| Варіант 9 (`variant_09_cybersecurity.xlsx`) | `Cybersecurity_Personnel` | `Cybersecurity_Tasks` | `Task_ID` |
| Варіант 10 (`variant_10_communications.xlsx`) | `Communication_Personnel` | `Communication_Units` | `Communication_Unit_ID` |
| Варіант 11 (`variant_11_personnel.xlsx`) | `Personnel` | `Personnel_Units` | `Unit_ID` |
| Варіант 12 (`variant_12_transport.xlsx`) | `Transport_Personnel` | `Vehicles` | `Vehicle_ID` |
| Варіант 13 (`variant_13_finance.xlsx`) | `Finance_Staff` | `Finance_Tasks` | `Finance_Task_ID` |
| Варіант 14 (`variant_14_ammunition.xlsx`) | `Ammunition_Personnel` | `Ammunition` | `Ammunition_ID` |
| Варіант 15 (`variant_15_energy.xlsx`) | `Energy_Personnel` | `Energy_Tasks` | `Energy_Task_ID` |
| Варіант 16 (`variant_16_missions.xlsx`) | `Mission_Staff` | `Missions` | `Mission_ID` |
| Варіант 17 (`variant_17_security.xlsx`) | `Security_Personnel` | `Security_Tasks` | `Security_Task_ID` |

## 2. Порядок розгортання та запуску
1. Запустіть скрипт `python run_task_2_5.py` для генерації 17 Excel-файлів у папці `data/`.
2. Скрипт автоматично імпортує всі листи Excel у реляційну базу даних та виконує 20 SQL-запитів.
3. SQL-код запитів зберігається у `sql_scripts/all_20_queries.sql`, а табличний звіт — у `results/queries_results.md`.
