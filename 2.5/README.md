# Звіт з виконання практичного заняття 2.5 (Реляційні бази даних ІАЗ ОУВ)

У проєкті реалізовано всі **17 варіантів** із методички `2.5.docx` (34 взаємопов'язані таблиці). Комплекс із 20 SQL-запитів виконано на базі найбільшого за структурою **Варіанта 16 (Моніторинг місій — 11 полів)** у поєднанні з аналітичними **Варіантом 8 (Медичне забезпечення)** та **Варіантом 13 (Фінансове забезпечення)**.

### 1. Отримати всі дані з таблиці особового складу місій Mission_Staff (Варіант 16)
```sql
SELECT * FROM Mission_Staff;
```
 ID          Name                          Role  Mission_ID Date_Assigned
  1 Ковальов С.П. Керівник групи планування J-3        1601    2026-08-25
  2   Бондар Д.А.        Офіцер координації ППО        1601    2026-09-01
  3 Марченко О.Ю.  Старший офіцер логістики J-4        1602    2026-09-28
  4  Лисенко І.В.          Командир загону БпЛА        1603    2026-10-12
  5 Павленко В.І. Офіцер взаємодії з артилерією        1603    2026-10-14
  6 Карпенко С.І.     Начальник евак. групи ОВТ        1604    2026-10-29

### 2. Отримати всі дані про оперативні місії та їхні цілі з таблиці Missions (Варіант 16)
```sql
SELECT Mission_ID, Mission_Name, Objective, Commander, Start_Date, End_Date FROM Missions;
```
 Mission_ID                Mission_Name                         Objective          Commander Start_Date   End_Date
       1601        Місія 'Небесний Щит'         Прикриття ППО в смузі ОУВ п-к Ковальчук О.М. 2026-09-01 2026-12-31
       1602 Місія 'Логістичний Коридор'      Охорона маршрутів постачання  п/п-к Гнатюк В.С. 2026-10-01 2026-11-30
       1603          Місія 'Очі Севера' Аеророзвідка та корегування вогню  м-р Шевченко Т.Г. 2026-10-15 2026-12-15
       1604    Місія 'Відновлення-Схід'  Евакуація та ремонт бронетехніки   п/п-к Токар С.М. 2026-11-01 2026-12-20

### 3. Фільтрація (WHERE >): Медичні підрозділи з місткістю понад 50 ліжко-місць та запасами > 1000 (Варіант 8)
```sql
SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units WHERE Capacity > 50 AND Supplies_Available > 1000;
```
                Unit_Name Base_Location  Capacity  Supplies_Available
ПХГ №1 (Хірургічна група)   Краматорськ        60                1450
 Військовий госпіталь №66        Дніпро       250                5400

### 4. Фільтрація бюджету (WHERE >): Фінансові завдання з бюджетом понад 3 000 000 грн (Варіант 13)
```sql
SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks WHERE Budget_Allocated > 3000000;
```
        Task_Description  Budget_Allocated        Assigned_Unit
   Закупівля БпЛА та FPV           4500000        Батальйон БпС
Грошове забезпечення О/С          12500000 Фінансова служба ОУВ

### 5. JOIN (Варіант 16): Зведення офіцерів штабу, їхніх ролей, назв місій та визначених цілей (Objective)
```sql
SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name, Missions.Objective, Missions.Commander FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID;
```
         Name                          Role                Mission_Name                         Objective          Commander
Ковальов С.П. Керівник групи планування J-3        Місія 'Небесний Щит'         Прикриття ППО в смузі ОУВ п-к Ковальчук О.М.
  Бондар Д.А.        Офіцер координації ППО        Місія 'Небесний Щит'         Прикриття ППО в смузі ОУВ п-к Ковальчук О.М.
Марченко О.Ю.  Старший офіцер логістики J-4 Місія 'Логістичний Коридор'      Охорона маршрутів постачання  п/п-к Гнатюк В.С.
 Лисенко І.В.          Командир загону БпЛА          Місія 'Очі Севера' Аеророзвідка та корегування вогню  м-р Шевченко Т.Г.
Павленко В.І. Офіцер взаємодії з артилерією          Місія 'Очі Севера' Аеророзвідка та корегування вогню  м-р Шевченко Т.Г.
Карпенко С.І.     Начальник евак. групи ОВТ    Місія 'Відновлення-Схід'  Евакуація та ремонт бронетехніки   п/п-к Токар С.М.

### 6. JOIN + WHERE (Варіант 16): Офіцери, залучені до конкретної місії ППО ('Місія ''Небесний Щит''')
```sql
SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID WHERE Missions.Mission_Name = 'Місія ''Небесний Щит''';
```
         Name                          Role         Mission_Name
  Бондар Д.А.        Офіцер координації ППО Місія 'Небесний Щит'
Ковальов С.П. Керівник групи планування J-3 Місія 'Небесний Щит'

### 7. GROUP BY + COUNT (Варіант 16): Кількість офіцерів штабу, закріплених за кожною місією
```sql
SELECT Missions.Mission_Name, COUNT(Mission_Staff.ID) AS Staff_Count FROM Missions LEFT JOIN Mission_Staff ON Missions.Mission_ID = Mission_Staff.Mission_ID GROUP BY Missions.Mission_Name;
```
               Mission_Name  Staff_Count
   Місія 'Відновлення-Схід'            1
Місія 'Логістичний Коридор'            1
       Місія 'Небесний Щит'            2
         Місія 'Очі Севера'            2

### 8. GROUP BY + AVG / SUM (Варіант 8): Середня місткість та сумарні медичні запаси за локаціями
```sql
SELECT Base_Location, AVG(Capacity) AS Avg_Capacity, SUM(Supplies_Available) AS Total_Supplies FROM Medical_Units GROUP BY Base_Location;
```
Base_Location  Avg_Capacity  Total_Supplies
       Дніпро         250.0            5400
  Краматорськ          60.0            1450
    Покровськ          40.0             920
   Слов'янськ          30.0             780

### 9. MAX (Варіант 13): Максимальний виділений бюджет серед фінансових завдань ОУВ
```sql
SELECT Task_Description, MAX(Budget_Allocated) AS Max_Budget FROM Finance_Tasks;
```
        Task_Description  Max_Budget
Грошове забезпечення О/С    12500000

### 10. Фільтрація за датою: Офіцери місій, призначені після 1 жовтня 2026 року (Варіант 16)
```sql
SELECT Name, Role, Date_Assigned FROM Mission_Staff WHERE Date_Assigned > '2026-10-01';
```
         Name                          Role Date_Assigned
 Лисенко І.В.          Командир загону БпЛА    2026-10-12
Павленко В.І. Офіцер взаємодії з артилерією    2026-10-14
Карпенко С.І.     Начальник евак. групи ОВТ    2026-10-29

### 11. ORDER BY DESC: Рейтинг медичних підрозділів за обсягом доступних медикаментів (Варіант 8)
```sql
SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units ORDER BY Supplies_Available DESC;
```
                Unit_Name Base_Location  Capacity  Supplies_Available
 Військовий госпіталь №66        Дніпро       250                5400
ПХГ №1 (Хірургічна група)   Краматорськ        60                1450
Стабілізаційний пункт ОУВ     Покровськ        40                 920
     Медична рота CASEVAC    Слов'янськ        30                 780

### 12. Підзапит (Subquery): Медичні підрозділи із запасами вище середнього показника по ОУВ (Варіант 8)
```sql
SELECT Unit_Name, Supplies_Available FROM Medical_Units WHERE Supplies_Available > (SELECT AVG(Supplies_Available) FROM Medical_Units);
```
               Unit_Name  Supplies_Available
Військовий госпіталь №66                5400

### 13. Підзапит (Subquery): Фінансові завдання з бюджетом вище середнього (Варіант 13)
```sql
SELECT Task_Description, Budget_Allocated FROM Finance_Tasks WHERE Budget_Allocated > (SELECT AVG(Budget_Allocated) FROM Finance_Tasks);
```
        Task_Description  Budget_Allocated
Грошове забезпечення О/С          12500000

### 14. COUNT: Загальна кількість залучених офіцерів у місіях ОУВ (Варіант 16)
```sql
SELECT COUNT(*) AS Total_Mission_Staff FROM Mission_Staff;
```
 Total_Mission_Staff
                   6

### 15. LIMIT 3: Топ-3 найбільш фінансовані завдання ОУВ (Варіант 13)
```sql
SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks ORDER BY Budget_Allocated DESC LIMIT 3;
```
        Task_Description  Budget_Allocated        Assigned_Unit
Грошове забезпечення О/С          12500000 Фінансова служба ОУВ
   Закупівля БпЛА та FPV           4500000        Батальйон БпС
     Ремонт бронетехніки           2800000                  РВБ

### 16. JOIN + Складна умова (Варіант 8): Медперсонал госпіталів та ПХГ із запасами > 1000
```sql
SELECT Medical_Staff.Name, Medical_Staff.Position, Medical_Units.Unit_Name, Medical_Units.Base_Location FROM Medical_Staff JOIN Medical_Units ON Medical_Staff.Medical_Unit_ID = Medical_Units.Medical_Unit_ID WHERE Medical_Units.Supplies_Available > 1000;
```
         Name             Position                 Unit_Name Base_Location
 Кравчук Д.І.         Анестезіолог ПХГ №1 (Хірургічна група)   Краматорськ
  Шевчук В.О.     Провідний хірург ПХГ №1 (Хірургічна група)   Краматорськ
Захарчук І.П.     Начальник аптеки  Військовий госпіталь №66        Дніпро
 Олійник Н.В. Операційна медсестра  Військовий госпіталь №66        Дніпро

### 17. INSERT (Варіант 16): Додавання нового офіцера до штабу моніторингу місій
```sql
INSERT INTO Mission_Staff (ID, Name, Role, Mission_ID, Date_Assigned) VALUES (7, 'Савчук І.В.', 'Старший інспектор безпеки польотів', 1601, '2026-11-05');
```
*Команду виконано успішно (змінено записів: 1).*

### 18. UPDATE (Варіант 16): Оновлення посади офіцера у таблиці Mission_Staff
```sql
UPDATE Mission_Staff SET Role = 'Начальник групи оперативного планування J-3' WHERE Name = 'Ковальов С.П.';
```
*Команду виконано успішно (змінено записів: 1).*

### 19. UPDATE (Варіант 8): Збільшення медичних запасів стабілізаційного пункту після підвозу
```sql
UPDATE Medical_Units SET Supplies_Available = 1500 WHERE Medical_Unit_ID = 802;
```
*Команду виконано успішно (змінено записів: 1).*

### 20. DELETE (Варіант 16): Видалення тестового запису з таблиці Mission_Staff за ID = 7
```sql
DELETE FROM Mission_Staff WHERE ID = 7;
```
*Команду виконано успішно (змінено записів: 1).*

