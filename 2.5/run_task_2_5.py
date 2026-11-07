import os
import sqlite3
import pandas as pd

# Автоматично визначаємо шлях до папки 2.5, де лежить цей скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Створення структури папок САМЕ всередині папки 2.5
for folder in ["sql_scripts", "data", "results", "docs"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# 2. Повний набір синтетичних даних для ВСІХ 17 ВАРІАНТІВ із методички 2.5.docx
all_17_variants = {
    "variant_01_officers_units.xlsx": {
        "Units": pd.DataFrame({
            "Unit_ID": [101, 102, 103, 104],
            "Unit_Name": ["1-й мех. батальйон", "2-й танковий батальйон", "Дивізіон ППО", "Батальйон БпС"],
            "Base_Location": ["Сектор А", "Сектор Б", "Сектор В", "Сектор А"],
            "Commander": ["п/п-к Коваленко О.В.", "м-р Мельник І.С.", "п/п-к Бондар Д.А.", "м-р Шевченко Т.Г."]
        }),
        "Officers": pd.DataFrame({
            "ID": [1, 2, 3, 4, 5, 6],
            "Name": ["Бойко А.С.", "Ткаченко М.І.", "Кравченко О.П.", "Савченко Д.М.", "Лисенко І.В.", "Мороз Є.В."],
            "Rank": ["Капітан", "Старший лейтенант", "Майор", "Лейтенант", "Капітан", "Старший лейтенант"],
            "Unit_ID": [101, 101, 102, 103, 104, 103],
            "Date_Assigned": ["2024-03-15", "2025-01-20", "2023-11-05", "2025-06-12", "2026-02-01", "2025-09-18"]
        })
    },
    "variant_02_logistics.xlsx": {
        "Logistics_Units": pd.DataFrame({
            "Logistics_Unit_ID": [201, 202, 203],
            "Logistics_Unit_Name": ["Рота мат. забезпечення", "Автобат підвозу ПММ", "Польовий склад РАО"],
            "Supplies_Available": [850, 1200, 640],
            "Base_Location": ["Хаб Північ", "Хаб Схід", "Тиловий район Б"]
        }),
        "Logistics_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Сидоренко П.І.", "Гаврилюк Р.О.", "Романюк В.С.", "Поліщук А.В."],
            "Position": ["Начальник складу ПММ", "Офіцер J-4", "Обліковець РАО", "Командир взводу підвозу"],
            "Logistics_Unit_ID": [202, 201, 203, 201],
            "Date_Assigned": ["2024-05-10", "2025-02-14", "2024-08-22", "2025-11-03"]
        })
    },
    "variant_03_operations.xlsx": {
        "Operations": pd.DataFrame({
            "Operation_ID": [301, 302, 303],
            "Operation_Name": ["Щит Півночі", "Сталевий Рубіж", "Небесний Вартовий"],
            "Commander": ["п-к Захарченко В.М.", "п-к Гриценко А.П.", "п/п-к Бондар Д.А."],
            "Operation_Start_Date": ["2026-01-10", "2026-05-01", "2026-09-01"],
            "Operation_End_Date": ["2026-04-15", "2026-08-30", "2026-12-15"]
        }),
        "Operations_Staff": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Марченко О.Ю.", "Клименко С.В.", "Павленко В.І.", "Руденко Б.О."],
            "Role": ["Офіцер J-3", "Аналітик J-2", "Офіцер вогневого ураження", "Офіцер координації ППО"],
            "Operation_ID": [301, 302, 302, 303],
            "Date_Assigned": ["2026-01-05", "2026-04-25", "2026-04-28", "2026-08-25"]
        })
    },
    "variant_04_equipment.xlsx": {
        "Equipment": pd.DataFrame({
            "Equipment_ID": [401, 402, 403, 404],
            "Equipment_Type": ["БМП-2", "БРЕМ-1", "Танк Т-64БВ", "КШМ Р-142Н"],
            "Condition": ["Боєготова", "Боєготова", "На ремонті", "Боєготова"],
            "Last_Inspection_Date": ["2026-10-15", "2026-10-20", "2026-09-30", "2026-11-01"]
        }),
        "Equipment_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Волошин Д.П.", "Карпенко С.І.", "Назаренко Ю.Г.", "Кузьменко І.Р."],
            "Role": ["Механік-водій", "Командир евак. відділення", "Інженер з ремонту", "Начальник радіостанції"],
            "Equipment_ID": [401, 402, 403, 404],
            "Assigned_Unit": ["1-й мех. батальйон", "РВБ", "РВБ", "Вузол зв'язку J-6"]
        })
    },
    "variant_05_weapons.xlsx": {
        "Weapons": pd.DataFrame({
            "Weapon_ID": [501, 502, 503, 504],
            "Weapon_Type": ["ПЗРК Stinger", "ПТРК Стугна-П", "ЗРК Gepard", "Міномет 120-мм"],
            "Ammunition_Available": [14, 28, 640, 120],
            "Last_Inspection_Date": ["2026-10-10", "2026-10-18", "2026-11-02", "2026-09-25"]
        }),
        "Weapons_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Гончарук Т.Л.", "Дмитренко В.О.", "Козак А.В.", "Білоус М.А."],
            "Rank": ["Старший солдат", "Сержант", "Молодший сержант", "Старший сержант"],
            "Weapon_ID": [501, 502, 503, 504],
            "Assigned_Unit": ["МВГ ППО", "ПТ взвод", "Дивізіон ППО", "Мінометна батарея"]
        })
    },
    "variant_06_training.xlsx": {
        "Training_Programs": pd.DataFrame({
            "Training_Program_ID": [601, 602, 603],
            "Program_Name": ["Планування операцій НАТО (OPP)", "Застосування ударних БпЛА", "Евакуація та відновлення ОВТ"],
            "Instructor": ["п-к Савчук І.В.", "к-н Лисенко І.В.", "п/п-к Токар С.М."],
            "Start_Date": ["2026-09-01", "2026-10-01", "2026-10-15"],
            "End_Date": ["2026-10-15", "2026-11-01", "2026-11-20"]
        }),
        "Training_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Ковальов С.П.", "Мельничук О.Б.", "Панченко А.Є.", "Тимошенко Г.Р."],
            "Rank": ["Майор", "Капітан", "Лейтенант", "Старший лейтенант"],
            "Training_Program_ID": [601, 601, 602, 603],
            "Date_Enrolled": ["2026-08-28", "2026-08-29", "2026-09-25", "2026-10-10"]
        })
    },
    "variant_07_intelligence.xlsx": {
        "Intelligence_Tasks": pd.DataFrame({
            "Task_ID": [701, 702, 703],
            "Task_Description": ["Супутниковий моніторинг ППО", "РЕР у смузі ОУВ", "Аналіз логістики противника"],
            "Priority": ["Високий", "Критичний", "Середній"],
            "Deadline": ["2026-11-15", "2026-11-10", "2026-11-25"],
            "Assigned_Unit": ["Аналітичний центр J-2", "Вузол РЕР", "Секція OSINT J-2"]
        }),
        "Intelligence_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Ковальчук І.П.", "Литвин О.С.", "Семенюк А.В.", "Бондаренко М.О."],
            "Rank": ["Майор", "Капітан", "Старший лейтенант", "Лейтенант"],
            "Task_ID": [701, 702, 702, 703],
            "Date_Assigned": ["2026-10-01", "2026-10-05", "2026-10-12", "2026-10-20"]
        })
    },
    "variant_08_medical.xlsx": {
        "Medical_Units": pd.DataFrame({
            "Medical_Unit_ID": [801, 802, 803, 804],
            "Unit_Name": ["ПХГ №1 (Хірургічна група)", "Стабілізаційний пункт ОУВ", "Військовий госпіталь №66", "Медична рота CASEVAC"],
            "Base_Location": ["Краматорськ", "Покровськ", "Дніпро", "Слов'янськ"],
            "Capacity": [60, 40, 250, 30],
            "Supplies_Available": [1450, 920, 5400, 780]
        }),
        "Medical_Staff": pd.DataFrame({
            "ID": [1, 2, 3, 4, 5, 6],
            "Name": ["Шевчук В.О.", "Кравчук Д.І.", "Мельник С.М.", "Олійник Н.В.", "Ткач Б.Р.", "Захарчук І.П."],
            "Position": ["Провідний хірург", "Анестезіолог", "Начальник стабпункту", "Операційна медсестра", "Парамедик", "Начальник аптеки"],
            "Medical_Unit_ID": [801, 801, 802, 803, 804, 803],
            "Date_Assigned": ["2025-03-10", "2025-06-15", "2024-11-20", "2025-01-12", "2026-02-05", "2024-08-01"]
        })
    },
    "variant_09_cybersecurity.xlsx": {
        "Cybersecurity_Tasks": pd.DataFrame({
            "Task_ID": [901, 902, 903],
            "Task_Description": ["Захист контуру АСУВ DELTA", "Аудит каналів VPN штабу", "Блокування фішингових атак"],
            "System_Affected": ["АСУВ DELTA", "Вузол спецзв'язку", "Поштовий шлюз"],
            "Risk_Level": ["Критичний", "Високий", "Середній"],
            "Deadline": ["2026-11-12", "2026-11-18", "2026-11-30"]
        }),
        "Cybersecurity_Personnel": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Григоренко О.В.", "Савчук Д.І.", "Коваленко Ю.С.", "Левченко А.П."],
            "Position": ["Спеціаліст CERT", "Інженер ЗІ", "Адміністратор безпеки", "Аналітик SOC"],
            "Task_ID": [901, 901, 902, 903],
            "Date_Assigned": ["2026-09-01", "2026-09-10", "2026-10-01", "2026-10-15"]
        })
    },
    "variant_10_communications.xlsx": {
        "Communication_Units": pd.DataFrame({
            "Communication_Unit_ID": [1001, 1002, 1003],
            "Unit_Name": ["Польовий вузол зв'язку КП", "Рота радіорелейного зв'язку", "Група супутникового зв'язку"],
            "Base_Location": ["Сектор А", "Сектор Б", "Передовий ПУ"],
            "Equipment_Available": [85, 42, 120]
        }),
        "Communication_Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Мазур І.С.", "Білик Р.О.", "Вовк В.А."],
            "Role": ["Начальник вузла зв'язку", "Інженер супутникових систем", "Радіотелеграфіст КШМ"],
            "Communication_Unit_ID": [1001, 1003, 1002],
            "Date_Assigned": ["2024-07-01", "2025-04-12", "2025-09-19"]
        })
    },
    "variant_11_personnel.xlsx": {
        "Personnel_Units": pd.DataFrame({
            "Unit_ID": [1101, 1102],
            "Unit_Name": ["Штаб ОУВ (Секція J-1)", "Резервний батальйон"],
            "Base_Location": ["Сектор Центру", "Тиловий район А"],
            "Commander": ["п-к Кравцов О.М.", "п/п-к Дяченко В.І."]
        }),
        "Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Соловей А.Г.", "Кушнір О.П.", "Москаленко П.Ю."],
            "Rank": ["Майор", "Капітан", "Старший лейтенант"],
            "Unit_ID": [1101, 1101, 1102],
            "Date_Assigned": ["2024-02-10", "2025-05-18", "2026-01-15"]
        })
    },
    "variant_12_transport.xlsx": {
        "Vehicles": pd.DataFrame({
            "Vehicle_ID": [1201, 1202, 1203],
            "Vehicle_Type": ["Тягач MAN HX81 (трал)", "Вантажівка КрАЗ-6322", "Паливозаправник МАЗ"],
            "Condition": ["Справний", "Справний", "Потребує ТО"],
            "Last_Inspection_Date": ["2026-10-25", "2026-10-12", "2026-09-18"],
            "Assigned_Unit": ["Взвод евакуації ОВТ", "Авторота підвозу БК", "Рота ПММ"]
        }),
        "Transport_Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Дорошенко М.В.", "Пилипенко С.І.", "Зінченко О.М."],
            "Position": ["Старший водій трала", "Водій-експедитор БК", "Водій паливозаправника"],
            "Vehicle_ID": [1201, 1202, 1203],
            "Date_Assigned": ["2025-03-01", "2025-07-14", "2024-11-30"]
        })
    },
    "variant_13_finance.xlsx": {
        "Finance_Tasks": pd.DataFrame({
            "Finance_Task_ID": [1301, 1302, 1303, 1304],
            "Task_Description": ["Закупівля БпЛА та FPV", "Ремонт бронетехніки", "Грошове забезпечення О/С", "Придбання генераторів"],
            "Budget_Allocated": [4500000.0, 2800000.0, 12500000.0, 950000.0],
            "Deadline": ["2026-11-20", "2026-12-01", "2026-11-10", "2026-11-25"],
            "Assigned_Unit": ["Батальйон БпС", "РВБ", "Фінансова служба ОУВ", "Інженерна служба"]
        }),
        "Finance_Staff": pd.DataFrame({
            "ID": [1, 2, 3, 4],
            "Name": ["Костенко Г.О.", "Юрченко В.В.", "Хмельницький І.Б.", "Симоненко О.С."],
            "Position": ["Начальник ФЕС", "Офіцер закупівель", "Бухгалтер-ревізор", "Фахівець з договорів"],
            "Finance_Task_ID": [1303, 1301, 1302, 1304],
            "Date_Assigned": ["2024-01-15", "2025-04-10", "2025-08-22", "2026-03-05"]
        })
    },
    "variant_14_ammunition.xlsx": {
        "Ammunition": pd.DataFrame({
            "Ammunition_ID": [1401, 1402, 1403],
            "Ammunition_Type": ["Снаряди 155-мм (M795)", "Зенітні ракети ПЗРК", "Танкові постріли 125-мм"],
            "Quantity": [1250, 85, 640],
            "Storage_Location": ["Польовий склад РАО №1", "Сектор ППО Північ", "Польовий склад РАО №2"],
            "Last_Inspection_Date": ["2026-10-30", "2026-11-02", "2026-10-18"]
        }),
        "Ammunition_Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Терещенко В.П.", "Черненко Д.О.", "Данилюк Р.І."],
            "Role": ["Начальник сховища РАО", "Технік ракетного озброєння", "Комірник БК"],
            "Ammunition_ID": [1401, 1402, 1403],
            "Assigned_Unit": ["Служба РАО ОУВ", "Дивізіон ППО", "Танковий батальйон"]
        })
    },
    "variant_15_energy.xlsx": {
        "Energy_Tasks": pd.DataFrame({
            "Energy_Task_ID": [1501, 1502, 1503],
            "Task_Description": ["Живлення КП ОУВ", "Зарядні станції для БпЛА", "Резервне живлення стабпункту"],
            "Energy_Source": ["Дизель-генератор 50 кВт", "Гібридна СЕС + LiFePO4", "Дизель-генератор 30 кВт"],
            "Deadline": ["2026-11-10", "2026-11-18", "2026-11-12"],
            "Assigned_Unit": ["Комендатура КП", "Батальйон БпС", "Медична рота"]
        }),
        "Energy_Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Яковенко П.С.", "Климчук А.В.", "Федоренко М.І."],
            "Role": ["Головний енергетик КП", "Електромеханік", "Спеціаліст АКБ"],
            "Energy_Task_ID": [1501, 1503, 1502],
            "Date_Assigned": ["2025-01-20", "2025-09-10", "2026-04-01"]
        })
    },
    "variant_16_missions.xlsx": {
        "Missions": pd.DataFrame({
            "Mission_ID": [1601, 1602, 1603, 1604],
            "Mission_Name": ["Місія 'Небесний Щит'", "Місія 'Логістичний Коридор'", "Місія 'Очі Севера'", "Місія 'Відновлення-Схід'"],
            "Objective": ["Прикриття ППО в смузі ОУВ", "Охорона маршрутів постачання", "Аеророзвідка та корегування вогню", "Евакуація та ремонт бронетехніки"],
            "Commander": ["п-к Ковальчук О.М.", "п/п-к Гнатюк В.С.", "м-р Шевченко Т.Г.", "п/п-к Токар С.М."],
            "Start_Date": ["2026-09-01", "2026-10-01", "2026-10-15", "2026-11-01"],
            "End_Date": ["2026-12-31", "2026-11-30", "2026-12-15", "2026-12-20"]
        }),
        "Mission_Staff": pd.DataFrame({
            "ID": [1, 2, 3, 4, 5, 6],
            "Name": ["Ковальов С.П.", "Бондар Д.А.", "Марченко О.Ю.", "Лисенко І.В.", "Павленко В.І.", "Карпенко С.І."],
            "Role": ["Керівник групи планування J-3", "Офіцер координації ППО", "Старший офіцер логістики J-4", "Командир загону БпЛА", "Офіцер взаємодії з артилерією", "Начальник евак. групи ОВТ"],
            "Mission_ID": [1601, 1601, 1602, 1603, 1603, 1604],
            "Date_Assigned": ["2026-08-25", "2026-09-01", "2026-09-28", "2026-10-12", "2026-10-14", "2026-10-29"]
        })
    },
    "variant_17_security.xlsx": {
        "Security_Tasks": pd.DataFrame({
            "Security_Task_ID": [1701, 1702, 1703],
            "Task_Description": ["Охорона та оборона КП ОУВ", "Контрдиверсійна перевірка тилу", "Контроль режиму таємності ПУ"],
            "Risk_Level": ["Високий", "Критичний", "Середній"],
            "Deadline": ["2026-12-31", "2026-11-15", "2026-11-20"],
            "Assigned_Unit": ["Рота охорони КП", "Зведена група ВСП", "Служба ОДТ"]
        }),
        "Security_Personnel": pd.DataFrame({
            "ID": [1, 2, 3],
            "Name": ["Кравець О.І.", "Литвиненко Б.М.", "Гончар Р.П."],
            "Position": ["Командир роти охорони", "Старший офіцер ВСП", "Офіцер РСО"],
            "Security_Task_ID": [1701, 1702, 1703],
            "Date_Assigned": ["2025-02-01", "2025-08-15", "2026-01-10"]
        })
    }
}

# Підключення до бази даних у папці 2.5/data/
db_path = os.path.join(BASE_DIR, "data", "iaz_all_17_variants.db")
conn = sqlite3.connect(db_path)

for filename, sheets in all_17_variants.items():
    filepath = os.path.join(BASE_DIR, "data", filename)
    
    # Спочатку записуємо та закриваємо Excel-файл
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    # Після збереження файлу читаємо дані з Excel та імпортуємо в БД
    for sheet_name in sheets.keys():
        df_from_excel = pd.read_excel(filepath, sheet_name=sheet_name, engine="openpyxl")
        df_from_excel.to_sql(sheet_name, conn, if_exists="replace", index=False)

print(f"✔ Усі 17 Excel-файлів створено в '{os.path.join(BASE_DIR, 'data')}' та 34 таблиці імпортовано в БД!")

# 3. 20 SQL-запитів на базі Варіанта 16 (Моніторинг місій), Варіанта 8 (Медицина) і Варіанта 13 (Фінанси)
queries = [
    ("1. Отримати всі дані з таблиці особового складу місій Mission_Staff (Варіант 16)",
     "SELECT * FROM Mission_Staff;"),
    ("2. Отримати всі дані про оперативні місії та їхні цілі з таблиці Missions (Варіант 16)",
     "SELECT Mission_ID, Mission_Name, Objective, Commander, Start_Date, End_Date FROM Missions;"),
    ("3. Фільтрація (WHERE >): Медичні підрозділи з місткістю понад 50 ліжко-місць та запасами > 1000 (Варіант 8)",
     "SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units WHERE Capacity > 50 AND Supplies_Available > 1000;"),
    ("4. Фільтрація бюджету (WHERE >): Фінансові завдання з бюджетом понад 3 000 000 грн (Варіант 13)",
     "SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks WHERE Budget_Allocated > 3000000;"),
    ("5. JOIN (Варіант 16): Зведення офіцерів штабу, їхніх ролей, назв місій та визначених цілей (Objective)",
     "SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name, Missions.Objective, Missions.Commander FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID;"),
    ("6. JOIN + WHERE (Варіант 16): Офіцери, залучені до конкретної місії ППО ('Місія ''Небесний Щит''')",
     "SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID WHERE Missions.Mission_Name = 'Місія ''Небесний Щит''';"),
    ("7. GROUP BY + COUNT (Варіант 16): Кількість офіцерів штабу, закріплених за кожною місією",
     "SELECT Missions.Mission_Name, COUNT(Mission_Staff.ID) AS Staff_Count FROM Missions LEFT JOIN Mission_Staff ON Missions.Mission_ID = Mission_Staff.Mission_ID GROUP BY Missions.Mission_Name;"),
    ("8. GROUP BY + AVG / SUM (Варіант 8): Середня місткість та сумарні медичні запаси за локаціями",
     "SELECT Base_Location, AVG(Capacity) AS Avg_Capacity, SUM(Supplies_Available) AS Total_Supplies FROM Medical_Units GROUP BY Base_Location;"),
    ("9. MAX (Варіант 13): Максимальний виділений бюджет серед фінансових завдань ОУВ",
     "SELECT Task_Description, MAX(Budget_Allocated) AS Max_Budget FROM Finance_Tasks;"),
    ("10. Фільтрація за датою: Офіцери місій, призначені після 1 жовтня 2026 року (Варіант 16)",
     "SELECT Name, Role, Date_Assigned FROM Mission_Staff WHERE Date_Assigned > '2026-10-01';"),
    ("11. ORDER BY DESC: Рейтинг медичних підрозділів за обсягом доступних медикаментів (Варіант 8)",
     "SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units ORDER BY Supplies_Available DESC;"),
    ("12. Підзапит (Subquery): Медичні підрозділи із запасами вище середнього показника по ОУВ (Варіант 8)",
     "SELECT Unit_Name, Supplies_Available FROM Medical_Units WHERE Supplies_Available > (SELECT AVG(Supplies_Available) FROM Medical_Units);"),
    ("13. Підзапит (Subquery): Фінансові завдання з бюджетом вище середнього (Варіант 13)",
     "SELECT Task_Description, Budget_Allocated FROM Finance_Tasks WHERE Budget_Allocated > (SELECT AVG(Budget_Allocated) FROM Finance_Tasks);"),
    ("14. COUNT: Загальна кількість залучених офіцерів у місіях ОУВ (Варіант 16)",
     "SELECT COUNT(*) AS Total_Mission_Staff FROM Mission_Staff;"),
    ("15. LIMIT 3: Топ-3 найбільш фінансовані завдання ОУВ (Варіант 13)",
     "SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks ORDER BY Budget_Allocated DESC LIMIT 3;"),
    ("16. JOIN + Складна умова (Варіант 8): Медперсонал госпіталів та ПХГ із запасами > 1000",
     "SELECT Medical_Staff.Name, Medical_Staff.Position, Medical_Units.Unit_Name, Medical_Units.Base_Location FROM Medical_Staff JOIN Medical_Units ON Medical_Staff.Medical_Unit_ID = Medical_Units.Medical_Unit_ID WHERE Medical_Units.Supplies_Available > 1000;"),
    ("17. INSERT (Варіант 16): Додавання нового офіцера до штабу моніторингу місій",
     "INSERT INTO Mission_Staff (ID, Name, Role, Mission_ID, Date_Assigned) VALUES (7, 'Савчук І.В.', 'Старший інспектор безпеки польотів', 1601, '2026-11-05');"),
    ("18. UPDATE (Варіант 16): Оновлення посади офіцера у таблиці Mission_Staff",
     "UPDATE Mission_Staff SET Role = 'Начальник групи оперативного планування J-3' WHERE Name = 'Ковальов С.П.';"),
    ("19. UPDATE (Варіант 8): Збільшення медичних запасів стабілізаційного пункту після підвозу",
     "UPDATE Medical_Units SET Supplies_Available = 1500 WHERE Medical_Unit_ID = 802;"),
    ("20. DELETE (Варіант 16): Видалення тестового запису з таблиці Mission_Staff за ID = 7",
     "DELETE FROM Mission_Staff WHERE ID = 7;")
]

sql_file_content = []
report_lines = [
    "# Звіт з виконання практичного заняття 2.5 (Реляційні бази даних ІАЗ ОУВ)\n\n",
    "У проєкті реалізовано всі **17 варіантів** із методички `2.5.docx` (34 взаємопов'язані таблиці). ",
    "Комплекс із 20 SQL-запитів виконано на базі найбільшого за структурою **Варіанта 16 (Моніторинг місій — 11 полів)** ",
    "у поєднанні з аналітичними **Варіантом 8 (Медичне забезпечення)** та **Варіантом 13 (Фінансове забезпечення)**.\n\n"
]

cursor = conn.cursor()
for title, sql in queries:
    sql_file_content.append(f"-- {title}\n{sql}\n")
    report_lines.append(f"### {title}\n```sql\n{sql}\n```\n")
    if sql.strip().upper().startswith("SELECT"):
        df_res = pd.read_sql_query(sql, conn)
        try:
            table_str = df_res.to_markdown(index=False)
        except Exception:
            table_str = df_res.to_string(index=False)
        report_lines.append(table_str + "\n\n")
    else:
        cursor.execute(sql)
        conn.commit()
        report_lines.append(f"*Команду виконано успішно (змінено записів: {cursor.rowcount}).*\n\n")

# Зберігаємо всі вихідні файли безпосередньо всередині папки 2.5
with open(os.path.join(BASE_DIR, "sql_scripts", "all_20_queries.sql"), "w", encoding="utf-8") as f:
    f.write("\n".join(sql_file_content))

with open(os.path.join(BASE_DIR, "results", "queries_results.md"), "w", encoding="utf-8") as f:
    f.write("".join(report_lines))

with open(os.path.join(BASE_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write("".join(report_lines))

conn.close()
print(f"✔ Усі 20 SQL-запитів виконано! Усі файли збережено всередині папки: {BASE_DIR}")

# 4. Генерація технічної документації у папку docs/ (щоб вона не була порожньою)
docs_content = [
    "# Технічна документація бази даних ІАЗ ОУВ (Заняття 2.5)\n\n",
    "## 1. Архітектура бази даних та опис варіантів\n",
    "База даних `iaz_all_17_variants.db` (та серверна версія у PostgreSQL) містить 34 взаємопов'язані таблиці для всіх 17 варіантів:\n\n",
    "| Варіант | Таблиця 1 (Персонал / Штаб) | Таблиця 2 (Підрозділи / Завдання / Об'єкти) | Ключ зв'язку (Foreign Key) |\n",
    "| :--- | :--- | :--- | :--- |\n"
]

for idx, (fname, sheets) in enumerate(all_17_variants.items(), start=1):
    t_names = list(sheets.keys())
    fk_col = [col for col in sheets[t_names[1]].columns if col.endswith("_ID") and col != "ID"]
    fk_name = fk_col[0] if fk_col else "Unit_ID"
    docs_content.append(f"| Варіант {idx} (`{fname}`) | `{t_names[1]}` | `{t_names[0]}` | `{fk_name}` |\n")

docs_content.append(
    "\n## 2. Порядок розгортання та запуску\n"
    "1. Запустіть скрипт `python run_task_2_5.py` для генерації 17 Excel-файлів у папці `data/`.\n"
    "2. Скрипт автоматично імпортує всі листи Excel у реляційну базу даних та виконує 20 SQL-запитів.\n"
    "3. SQL-код запитів зберігається у `sql_scripts/all_20_queries.sql`, а табличний звіт — у `results/queries_results.md`.\n"
)

with open(os.path.join(BASE_DIR, "docs", "database_schema.md"), "w", encoding="utf-8") as f:
    f.write("".join(docs_content))

print("✔ Технічну документацію збережено у '2.5/docs/database_schema.md'!")