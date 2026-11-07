-- 1. Отримати всі дані з таблиці особового складу місій Mission_Staff (Варіант 16)
SELECT * FROM Mission_Staff;

-- 2. Отримати всі дані про оперативні місії та їхні цілі з таблиці Missions (Варіант 16)
SELECT Mission_ID, Mission_Name, Objective, Commander, Start_Date, End_Date FROM Missions;

-- 3. Фільтрація (WHERE >): Медичні підрозділи з місткістю понад 50 ліжко-місць та запасами > 1000 (Варіант 8)
SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units WHERE Capacity > 50 AND Supplies_Available > 1000;

-- 4. Фільтрація бюджету (WHERE >): Фінансові завдання з бюджетом понад 3 000 000 грн (Варіант 13)
SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks WHERE Budget_Allocated > 3000000;

-- 5. JOIN (Варіант 16): Зведення офіцерів штабу, їхніх ролей, назв місій та визначених цілей (Objective)
SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name, Missions.Objective, Missions.Commander FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID;

-- 6. JOIN + WHERE (Варіант 16): Офіцери, залучені до конкретної місії ППО ('Місія ''Небесний Щит''')
SELECT Mission_Staff.Name, Mission_Staff.Role, Missions.Mission_Name FROM Mission_Staff JOIN Missions ON Mission_Staff.Mission_ID = Missions.Mission_ID WHERE Missions.Mission_Name = 'Місія ''Небесний Щит''';

-- 7. GROUP BY + COUNT (Варіант 16): Кількість офіцерів штабу, закріплених за кожною місією
SELECT Missions.Mission_Name, COUNT(Mission_Staff.ID) AS Staff_Count FROM Missions LEFT JOIN Mission_Staff ON Missions.Mission_ID = Mission_Staff.Mission_ID GROUP BY Missions.Mission_Name;

-- 8. GROUP BY + AVG / SUM (Варіант 8): Середня місткість та сумарні медичні запаси за локаціями
SELECT Base_Location, AVG(Capacity) AS Avg_Capacity, SUM(Supplies_Available) AS Total_Supplies FROM Medical_Units GROUP BY Base_Location;

-- 9. MAX (Варіант 13): Максимальний виділений бюджет серед фінансових завдань ОУВ
SELECT Task_Description, MAX(Budget_Allocated) AS Max_Budget FROM Finance_Tasks;

-- 10. Фільтрація за датою: Офіцери місій, призначені після 1 жовтня 2026 року (Варіант 16)
SELECT Name, Role, Date_Assigned FROM Mission_Staff WHERE Date_Assigned > '2026-10-01';

-- 11. ORDER BY DESC: Рейтинг медичних підрозділів за обсягом доступних медикаментів (Варіант 8)
SELECT Unit_Name, Base_Location, Capacity, Supplies_Available FROM Medical_Units ORDER BY Supplies_Available DESC;

-- 12. Підзапит (Subquery): Медичні підрозділи із запасами вище середнього показника по ОУВ (Варіант 8)
SELECT Unit_Name, Supplies_Available FROM Medical_Units WHERE Supplies_Available > (SELECT AVG(Supplies_Available) FROM Medical_Units);

-- 13. Підзапит (Subquery): Фінансові завдання з бюджетом вище середнього (Варіант 13)
SELECT Task_Description, Budget_Allocated FROM Finance_Tasks WHERE Budget_Allocated > (SELECT AVG(Budget_Allocated) FROM Finance_Tasks);

-- 14. COUNT: Загальна кількість залучених офіцерів у місіях ОУВ (Варіант 16)
SELECT COUNT(*) AS Total_Mission_Staff FROM Mission_Staff;

-- 15. LIMIT 3: Топ-3 найбільш фінансовані завдання ОУВ (Варіант 13)
SELECT Task_Description, Budget_Allocated, Assigned_Unit FROM Finance_Tasks ORDER BY Budget_Allocated DESC LIMIT 3;

-- 16. JOIN + Складна умова (Варіант 8): Медперсонал госпіталів та ПХГ із запасами > 1000
SELECT Medical_Staff.Name, Medical_Staff.Position, Medical_Units.Unit_Name, Medical_Units.Base_Location FROM Medical_Staff JOIN Medical_Units ON Medical_Staff.Medical_Unit_ID = Medical_Units.Medical_Unit_ID WHERE Medical_Units.Supplies_Available > 1000;

-- 17. INSERT (Варіант 16): Додавання нового офіцера до штабу моніторингу місій
INSERT INTO Mission_Staff (ID, Name, Role, Mission_ID, Date_Assigned) VALUES (7, 'Савчук І.В.', 'Старший інспектор безпеки польотів', 1601, '2026-11-05');

-- 18. UPDATE (Варіант 16): Оновлення посади офіцера у таблиці Mission_Staff
UPDATE Mission_Staff SET Role = 'Начальник групи оперативного планування J-3' WHERE Name = 'Ковальов С.П.';

-- 19. UPDATE (Варіант 8): Збільшення медичних запасів стабілізаційного пункту після підвозу
UPDATE Medical_Units SET Supplies_Available = 1500 WHERE Medical_Unit_ID = 802;

-- 20. DELETE (Варіант 16): Видалення тестового запису з таблиці Mission_Staff за ID = 7
DELETE FROM Mission_Staff WHERE ID = 7;
