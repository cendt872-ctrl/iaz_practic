-- Очищення старих таблиць (якщо запускаєте повторно)
DROP TABLE IF EXISTS Officers, Units, Logistics_Personnel, Logistics_Units, Operations_Staff, Operations, Equipment_Personnel, Equipment, Weapons_Personnel, Weapons, Training_Personnel, Training_Programs CASCADE;

-- =========================================================================
-- ВАРІАНТ 1: ОПЕРАТИВНІ ПІДРОЗДІЛИ (Units та Officers)
-- =========================================================================
CREATE TABLE Units (
    Unit_ID INT PRIMARY KEY,
    Unit_Name VARCHAR(100),
    Base_Location VARCHAR(100),
    Commander VARCHAR(100)
);

CREATE TABLE Officers (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Unit_ID INT REFERENCES Units(Unit_ID),
    Date_Assigned DATE
);

INSERT INTO Units (Unit_ID, Unit_Name, Base_Location, Commander) VALUES
(101, '1-й механізований батальйон', 'Сектор А (Слов''янськ)', 'підполковник Коваленко О.В.'),
(102, '2-й танковий батальйон', 'Сектор Б (Краматорськ)', 'майор Мельник І.С.'),
(103, 'Дивізіон ППО', 'Сектор В (Покровськ)', 'підполковник Бондар Д.А.'),
(104, 'Батальйон безпілотних систем', 'Сектор А (Слов''янськ)', 'майор Шевченко Т.Г.');

INSERT INTO Officers (Name, Rank, Unit_ID, Date_Assigned) VALUES
('Бойко Андрій Сергійович', 'Капітан', 101, '2024-03-15'),
('Ткаченко Максим Ігорович', 'Старший лейтенант', 101, '2025-01-20'),
('Кравченко Олег Петрович', 'Майор', 102, '2023-11-05'),
('Савченко Дмитро Миколайович', 'Лейтенант', 103, '2025-06-12'),
('Лисенко Ігор Володимирович', 'Капітан', 104, '2026-02-01'),
('Мороз Євгеній Вікторович', 'Старший лейтенант', 103, '2025-09-18');

-- =========================================================================
-- ВАРІАНТ 2: ЛОГІСТИЧНЕ ЗАБЕЗПЕЧЕННЯ (Logistics_Units та Logistics_Personnel)
-- =========================================================================
CREATE TABLE Logistics_Units (
    Logistics_Unit_ID INT PRIMARY KEY,
    Logistics_Unit_Name VARCHAR(100),
    Supplies_Available INT,
    Base_Location VARCHAR(100)
);

CREATE TABLE Logistics_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Logistics_Unit_ID INT REFERENCES Logistics_Units(Logistics_Unit_ID),
    Date_Assigned DATE
);

INSERT INTO Logistics_Units VALUES
(201, 'Рота матеріального забезпечення', 850, 'Логістичний хаб Північ'),
(202, 'Автомобільний батальйон підвозу ПММ', 1200, 'Логістичний хаб Схід'),
(203, 'Польовий склад РАО', 640, 'Тиловий район Б');

INSERT INTO Logistics_Personnel (Name, Position, Logistics_Unit_ID, Date_Assigned) VALUES
('Сидоренко Павло Іванович', 'Начальник складу ПММ', 202, '2024-05-10'),
('Гаврилюк Роман Олегович', 'Офіцер відділення логістики J-4', 201, '2025-02-14'),
('Романюк Віктор Степанович', 'Обліковець РАО', 203, '2024-08-22'),
('Поліщук Артем Вадимович', 'Командир взводу підвозу', 201, '2025-11-03');

-- =========================================================================
-- ВАРІАНТ 3: ПЛАНУВАННЯ ОПЕРАЦІЙ (Operations та Operations_Staff)
-- =========================================================================
CREATE TABLE Operations (
    Operation_ID INT PRIMARY KEY,
    Operation_Name VARCHAR(100),
    Commander VARCHAR(100),
    Operation_Start_Date DATE,
    Operation_End_Date DATE
);

CREATE TABLE Operations_Staff (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Operation_ID INT REFERENCES Operations(Operation_ID),
    Date_Assigned DATE
);

INSERT INTO Operations VALUES
(301, 'Операція "Щит Півночі"', 'полковник Захарченко В.М.', '2026-01-10', '2026-04-15'),
(302, 'Операція "Сталевий Рубіж"', 'полковник Гриценко А.П.', '2026-05-01', '2026-08-30'),
(303, 'Операція "Небесний Вартовий"', 'підполковник Бондар Д.А.', '2026-09-01', '2026-12-15');

INSERT INTO Operations_Staff (Name, Role, Operation_ID, Date_Assigned) VALUES
('Марченко Олексій Юрійович', 'Старший офіцер J-3 (Операції)', 301, '2026-01-05'),
('Клименко Сергій Віталійович', 'Аналітик розвідки J-2', 302, '2026-04-25'),
('Павленко Вадим Ігорович', 'Офіцер планування вогневого ураження', 302, '2026-04-28'),
('Руденко Богдан Олександрович', 'Офіцер координації ППО', 303, '2026-08-25');

-- =========================================================================
-- ВАРІАНТ 4: ОБЛІК ТЕХНІКИ (Equipment та Equipment_Personnel)
-- =========================================================================
CREATE TABLE Equipment (
    Equipment_ID INT PRIMARY KEY,
    Equipment_Type VARCHAR(100),
    Condition VARCHAR(50),
    Last_Inspection_Date DATE
);

CREATE TABLE Equipment_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Equipment_ID INT REFERENCES Equipment(Equipment_ID),
    Assigned_Unit VARCHAR(100)
);

INSERT INTO Equipment VALUES
(401, 'БМП-2', 'Боєготова', '2026-10-15'),
(402, 'БРЕМ-1 (Евакуаційна)', 'Боєготова', '2026-10-20'),
(403, 'Танк Т-64БВ', 'На поточному ремонті', '2026-09-30'),
(404, 'КШМ Р-142Н', 'Боєготова', '2026-11-01');

INSERT INTO Equipment_Personnel (Name, Role, Equipment_ID, Assigned_Unit) VALUES
('Волошин Денис Петрович', 'Механік-водій', 401, '1-й мех. батальйон'),
('Карпенко Станіслав Ілліч', 'Командир евакуаційного відділення', 402, 'РВБ (Ремонтний батальйон)'),
('Назаренко Юрій Глібович', 'Інженер з ремонту бронетехніки', 403, 'РВБ (Ремонтний батальйон)'),
('Кузьменко Ілля Романович', 'Начальник радіостанції', 404, 'Вузол зв''язку J-6');

-- =========================================================================
-- ВАРІАНТ 5: ОБЛІК ОЗБРОЄННЯ (Weapons та Weapons_Personnel)
-- =========================================================================
CREATE TABLE Weapons (
    Weapon_ID INT PRIMARY KEY,
    Weapon_Type VARCHAR(100),
    Ammunition_Available INT,
    Last_Inspection_Date DATE
);

CREATE TABLE Weapons_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Weapon_ID INT REFERENCES Weapons(Weapon_ID),
    Assigned_Unit VARCHAR(100)
);

INSERT INTO Weapons VALUES
(501, 'ПЗРК Stinger', 14, '2026-10-10'),
(502, 'ПТРК Стугна-П', 28, '2026-10-18'),
(503, 'ЗРК Gepard (35-мм)', 640, '2026-11-02'),
(504, 'Міномет 120-мм', 120, '2026-09-25');

INSERT INTO Weapons_Personnel (Name, Rank, Weapon_ID, Assigned_Unit) VALUES
('Гончарук Тарас Леонідович', 'Старший солдат', 501, 'Мобільна вогнева група ППО'),
('Дмитренко Віталій Олегович', 'Сержант', 502, 'Протитанковий взвод'),
('Козак Антон Васильович', 'Молодший сержант', 503, 'Дивізіон ППО'),
('Білоус Микола Андрійович', 'Старший сержант', 504, 'Мінометна батарея');

-- =========================================================================
-- ВАРІАНТ 6: ВІЙСЬКОВІ НАВЧАННЯ (Training_Programs та Training_Personnel)
-- =========================================================================
CREATE TABLE Training_Programs (
    Training_Program_ID INT PRIMARY KEY,
    Program_Name VARCHAR(100),
    Instructor VARCHAR(100),
    Start_Date DATE,
    End_Date DATE
);

CREATE TABLE Training_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Training_Program_ID INT REFERENCES Training_Programs(Training_Program_ID),
    Date_Enrolled DATE
);

INSERT INTO Training_Programs VALUES
(601, 'Планування операцій за стандартами НАТО (OPP / MDMP)', 'полковник Савчук І.В.', '2026-09-01', '2026-10-15'),
(602, 'Застосування тактичних ударних БпЛА', 'капітан Лисенко І.В.', '2026-10-01', '2026-11-01'),
(603, 'Організація евакуації та відновлення ОВТ', 'підполковник Токар С.М.', '2026-10-15', '2026-11-20');

INSERT INTO Training_Personnel (Name, Rank, Training_Program_ID, Date_Enrolled) VALUES
('Ковальов Сергій Павлович', 'Майор', 601, '2026-08-28'),
('Мельничук Орест Богданович', 'Капітан', 601, '2026-08-29'),
('панченко Артур Євгенович', 'Лейтенант', 602, '2026-09-25'),
('Тимошенко Гліб Романович', 'Старший лейтенант', 603, '2026-10-10');

-- Очищення таблиць варіантів 7-17 (якщо запускаєте повторно)
DROP TABLE IF EXISTS 
    Intelligence_Personnel, Intelligence_Tasks,
    Medical_Staff, Medical_Units,
    Cybersecurity_Personnel, Cybersecurity_Tasks,
    Communication_Personnel, Communication_Units,
    Personnel, Personnel_Units,
    Transport_Personnel, Vehicles,
    Finance_Staff, Finance_Tasks,
    Ammunition_Personnel, Ammunition,
    Energy_Personnel, Energy_Tasks,
    Mission_Staff, Missions,
    Security_Personnel, Security_Tasks CASCADE;

-- =========================================================================
-- ВАРІАНТ 7: РОЗВІДКА І АНАЛІЗ (J-2)
-- =========================================================================
CREATE TABLE Intelligence_Tasks (
    Task_ID INT PRIMARY KEY,
    Task_Description VARCHAR(150),
    Priority VARCHAR(50),
    Deadline DATE,
    Assigned_Unit VARCHAR(100)
);

CREATE TABLE Intelligence_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Task_ID INT REFERENCES Intelligence_Tasks(Task_ID),
    Date_Assigned DATE
);

INSERT INTO Intelligence_Tasks VALUES
(701, 'Супутниковий моніторинг позицій ППО противника', 'Високий', '2026-11-15', 'Аналітичний центр J-2'),
(702, 'Радіоелектронна розвідка у смузі відповідальності ОУВ', 'Критичний', '2026-11-10', 'Вузол РЕР'),
(703, 'Аналіз логістичних маршрутів постачання БК', 'Середній', '2026-11-25', 'Секція OSINT J-2');

INSERT INTO Intelligence_Personnel (Name, Rank, Task_ID, Date_Assigned) VALUES
('Ковальчук Ігор Петрович', 'Майор', 701, '2026-10-01'),
('Литвин Олена Сергіївна', 'Капітан', 702, '2026-10-05'),
('Семенюк Андрій Вікторович', 'Старший лейтенант', 702, '2026-10-12'),
('Бондаренко Максим Олегович', 'Лейтенант', 703, '2026-10-20');

-- =========================================================================
-- ВАРІАНТ 8: МЕДИЧНЕ ЗАБЕЗПЕЧЕННЯ (Найкращий аналітичний варіант)
-- =========================================================================
CREATE TABLE Medical_Units (
    Medical_Unit_ID INT PRIMARY KEY,
    Unit_Name VARCHAR(100),
    Base_Location VARCHAR(100),
    Capacity INT,
    Supplies_Available INT
);

CREATE TABLE Medical_Staff (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Medical_Unit_ID INT REFERENCES Medical_Units(Medical_Unit_ID),
    Date_Assigned DATE
);

INSERT INTO Medical_Units VALUES
(801, 'Передова хірургічна група №1 (ПХГ)', 'Краматорськ', 60, 1450),
(802, 'Стабілізаційний пункт ОУВ "Схід"', 'Покровськ', 40, 920),
(803, 'Військовий мобільний госпіталь №66', 'Дніпро (Тиловий район)', 250, 5400),
(804, 'Медична рота евакуації (CASEVAC)', 'Слов''янськ', 30, 780);

INSERT INTO Medical_Staff (Name, Position, Medical_Unit_ID, Date_Assigned) VALUES
('Шевчук Вікторія Олександрівна', 'Провідний хірург', 801, '2025-03-10'),
('Кравчук Дмитро Іванович', 'Лікар-анестезіолог', 801, '2025-06-15'),
('Мельник Сергій Миколайович', 'Начальник стабпункту', 802, '2024-11-20'),
('Олійник Наталія Василівна', 'Операційна медсестра', 803, '2025-01-12'),
('Ткач Богдан Романович', 'Парамедик евакуаційної бригади', 804, '2026-02-05'),
('Захарчук Ірина Петрівна', 'Начальник аптечного складу', 803, '2024-08-01');

-- =========================================================================
-- ВАРІАНТ 9: КІБЕРБЕЗПЕКА
-- =========================================================================
CREATE TABLE Cybersecurity_Tasks (
    Task_ID INT PRIMARY KEY,
    Task_Description VARCHAR(150),
    System_Affected VARCHAR(100),
    Risk_Level VARCHAR(50),
    Deadline DATE
);

CREATE TABLE Cybersecurity_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Task_ID INT REFERENCES Cybersecurity_Tasks(Task_ID),
    Date_Assigned DATE
);

INSERT INTO Cybersecurity_Tasks VALUES
(901, 'Захист контуру обміну даними системи DELTA', 'АСУВ DELTA', 'Критичний', '2026-11-12'),
(902, 'Аудит захищених каналів VPN штабу ОУВ', 'Вузол спецзв''язку', 'Високий', '2026-11-18'),
(903, 'Блокування фішингових атак на поштові сервери', 'Поштовий шлюз', 'Середній', '2026-11-30');

INSERT INTO Cybersecurity_Personnel (Name, Position, Task_ID, Date_Assigned) VALUES
('Григоренко Олексій Вадимович', 'Провідний спеціаліст CERT', 901, '2026-09-01'),
('Савчук Денис Ігорович', 'Інженер захисту інформації', 901, '2026-09-10'),
('Коваленко Юрій Сергійович', 'Адміністратор безпеки мереж', 902, '2026-10-01'),
('Левченко Артем Петрович', 'Аналітик SOC', 903, '2026-10-15');

-- =========================================================================
-- ВАРІАНТ 10: ЗВ'ЯЗОК І КОМУНІКАЦІЇ (J-6)
-- =========================================================================
CREATE TABLE Communication_Units (
    Communication_Unit_ID INT PRIMARY KEY,
    Unit_Name VARCHAR(100),
    Base_Location VARCHAR(100),
    Equipment_Available INT
);

CREATE TABLE Communication_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Communication_Unit_ID INT REFERENCES Communication_Units(Communication_Unit_ID),
    Date_Assigned DATE
);

INSERT INTO Communication_Units VALUES
(1001, 'Польовий вузол зв''язку КП ОУВ', 'Сектор А', 85),
(1002, 'Рота радіорелейного та тропосферного зв''язку', 'Сектор Б', 42),
(1003, 'Група супутникового зв''язку (Starlink / Tooway)', 'Передовий ПУ', 120);

INSERT INTO Communication_Personnel (Name, Role, Communication_Unit_ID, Date_Assigned) VALUES
('Мазур Іван Степанович', 'Начальник вузла зв''язку', 1001, '2024-07-01'),
('Білик Роман Олексійович', 'Інженер супутникових систем', 1003, '2025-04-12'),
('Вовк Віталій Андрійович', 'Радіотелеграфіст КШМ', 1002, '2025-09-19');

-- =========================================================================
-- ВАРІАНТ 11: ОБЛІК ОСОБОВОГО СКЛАДУ (J-1)
-- =========================================================================
CREATE TABLE Personnel_Units (
    Unit_ID INT PRIMARY KEY,
    Unit_Name VARCHAR(100),
    Base_Location VARCHAR(100),
    Commander VARCHAR(100)
);

CREATE TABLE Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Rank VARCHAR(50),
    Unit_ID INT REFERENCES Personnel_Units(Unit_ID),
    Date_Assigned DATE
);

INSERT INTO Personnel_Units VALUES
(1101, 'Штаб ОУВ (Секція J-1)', 'Сектор Центру', 'полковник Кравцов О.М.'),
(1102, 'Резервний батальйон поповнення', 'Тиловий район А', 'підполковник Дяченко В.І.');

INSERT INTO Personnel (Name, Rank, Unit_ID, Date_Assigned) VALUES
('Соловей Андрій Григорович', 'Майор', 1101, '2024-02-10'),
('Кушнір Олександр Петрович', 'Капітан', 1101, '2025-05-18'),
('Москаленко Павло Юрійович', 'Старший лейтенант', 1102, '2026-01-15');

-- =========================================================================
-- ВАРІАНТ 12: ТРАНСПОРТНЕ ЗАБЕЗПЕЧЕННЯ
-- =========================================================================
CREATE TABLE Vehicles (
    Vehicle_ID INT PRIMARY KEY,
    Vehicle_Type VARCHAR(100),
    Condition VARCHAR(50),
    Last_Inspection_Date DATE,
    Assigned_Unit VARCHAR(100)
);

CREATE TABLE Transport_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Vehicle_ID INT REFERENCES Vehicles(Vehicle_ID),
    Date_Assigned DATE
);

INSERT INTO Vehicles VALUES
(1201, 'Тягач MAN HX81 (трал для бронетехніки)', 'Справний', '2026-10-25', 'Взвод евакуації ОВТ'),
(1202, 'Вантажівка КрАЗ-6322', 'Справний', '2026-10-12', 'Авторота підвозу БК'),
(1203, 'Паливозаправник МАЗ-5337', 'Потребує ТО', '2026-09-18', 'Рота ПММ');

INSERT INTO Transport_Personnel (Name, Position, Vehicle_ID, Date_Assigned) VALUES
('Дорошенко Микола Васильович', 'Старший водій трала', 1201, '2025-03-01'),
('Пилипенко Сергій Іванович', 'Водій-експедитор БК', 1202, '2025-07-14'),
('Зінченко Олексій Миколайович', 'Водій паливозаправника', 1203, '2024-11-30');

-- =========================================================================
-- ВАРІАНТ 13: ФІНАНСОВЕ ЗАБЕЗПЕЧЕННЯ (J-8)
-- =========================================================================
CREATE TABLE Finance_Tasks (
    Finance_Task_ID INT PRIMARY KEY,
    Task_Description VARCHAR(150),
    Budget_Allocated DECIMAL(12, 2),
    Deadline DATE,
    Assigned_Unit VARCHAR(100)
);

CREATE TABLE Finance_Staff (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Finance_Task_ID INT REFERENCES Finance_Tasks(Finance_Task_ID),
    Date_Assigned DATE
);

INSERT INTO Finance_Tasks VALUES
(1301, 'Закупівля комплектуючих для FPV та БпЛА', 4500000.00, '2026-11-20', 'Батальйон БпС'),
(1302, 'Фінансування поточного ремонту бронетехніки', 2800000.00, '2026-12-01', 'РВБ'),
(1303, 'Виплата додаткової винагороди особовому складу', 12500000.00, '2026-11-10', 'Фінансова служба ОУВ'),
(1304, 'Придбання дизельних генераторів та інверторів', 950000.00, '2026-11-25', 'Інженерна служба');

INSERT INTO Finance_Staff (Name, Position, Finance_Task_ID, Date_Assigned) VALUES
('Костенко Ганна Олександрівна', 'Начальник фінансово-економічної служби', 1303, '2024-01-15'),
('Юрченко Вадим Вікторович', 'Старший офіцер з оборонних закупівель', 1301, '2025-04-10'),
('Хмельницький Ігор Богданович', 'Бухгалтер-ревізор МТЗ', 1302, '2025-08-22'),
('Симоненко Ольга Сергіївна', 'Фахівець з договірної роботи', 1304, '2026-03-05');

-- =========================================================================
-- ВАРІАНТ 14: ОБЛІК БОЄПРИПАСІВ
-- =========================================================================
CREATE TABLE Ammunition (
    Ammunition_ID INT PRIMARY KEY,
    Ammunition_Type VARCHAR(100),
    Quantity INT,
    Storage_Location VARCHAR(100),
    Last_Inspection_Date DATE
);

CREATE TABLE Ammunition_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Ammunition_ID INT REFERENCES Ammunition(Ammunition_ID),
    Assigned_Unit VARCHAR(100)
);

INSERT INTO Ammunition VALUES
(1401, 'Артилерійські постріли 155-мм (M795)', 1250, 'Польовий склад РАО №1', '2026-10-30'),
(1402, 'Зенітні ракети ПЗРК / ЗРК малої дальності', 85, 'Сектор ППО "Північ"', '2026-11-02'),
(1403, 'Танкові постріли 125-мм (уламково-фугасні)', 640, 'Польовий склад РАО №2', '2026-10-18');

INSERT INTO Ammunition_Personnel (Name, Role, Ammunition_ID, Assigned_Unit) VALUES
('Терещенко Віктор Павлович', 'Начальник сховища РАО', 1401, 'Служба РАО ОУВ'),
('Черненко Денис Олегович', 'Технік з обліку ракетного озброєння', 1402, 'Дивізіон ППО'),
('Данилюк Руслан Ігорович', 'Комірник боєприпасів', 1403, 'Танковий батальйон');

-- =========================================================================
-- ВАРІАНТ 15: ЕНЕРГЕТИЧНЕ ЗАБЕЗПЕЧЕННЯ
-- =========================================================================
CREATE TABLE Energy_Tasks (
    Energy_Task_ID INT PRIMARY KEY,
    Task_Description VARCHAR(150),
    Energy_Source VARCHAR(100),
    Deadline DATE,
    Assigned_Unit VARCHAR(100)
);

CREATE TABLE Energy_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Energy_Task_ID INT REFERENCES Energy_Tasks(Energy_Task_ID),
    Date_Assigned DATE
);

INSERT INTO Energy_Tasks VALUES
(1501, 'Забезпечення безперебійного живлення КП ОУВ', 'Дизель-генератор 50 кВт + EcoFlow Pro', '2026-11-10', 'Комендатура КП'),
(1502, 'Розгортання автономних зарядних станцій для БпЛА', 'Гібридна СЕС + АКБ LiFePO4', '2026-11-18', 'Батальйон БпС'),
(1503, 'Резервне живлення стабілізаційного медичного пункту', 'Дизель-генератор 30 кВт', '2026-11-12', 'Медична рота');

INSERT INTO Energy_Personnel (Name, Role, Energy_Task_ID, Date_Assigned) VALUES
('Яковенко Петро Степанович', 'Головний енергетик КП', 1501, '2025-01-20'),
('Климчук Артур Васильович', 'Електромеханік дизельних станцій', 1503, '2025-09-10'),
('Федоренко Максим Ігорович', 'Спеціаліст з акумуляторних систем', 1502, '2026-04-01');

-- =========================================================================
-- ВАРІАНТ 16: МОНІТОРИНГ МІСІЙ (Найбільший варіант — 11 полів)
-- =========================================================================
CREATE TABLE Missions (
    Mission_ID INT PRIMARY KEY,
    Mission_Name VARCHAR(100),
    Objective VARCHAR(200),
    Commander VARCHAR(100),
    Start_Date DATE,
    End_Date DATE
);

CREATE TABLE Mission_Staff (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Role VARCHAR(100),
    Mission_ID INT REFERENCES Missions(Mission_ID),
    Date_Assigned DATE
);

INSERT INTO Missions VALUES
(1601, 'Місія "Небесний Щит"', 'Прикриття повітряного простору та критичної інфраструктури в смузі ОУВ', 'полковник Ковальчук О.М.', '2026-09-01', '2026-12-31'),
(1602, 'Місія "Логістичний Коридор"', 'Інженерне обладнання та охорона маршрутів постачання та евакуації ОВТ', 'підполковник Гнатюк В.С.', '2026-10-01', '2026-11-30'),
(1603, 'Місія "Очі Севера"', 'Цілодобова аеророзвідка та корегування вогню артилерії у визначеному секторі', 'майор Шевченко Т.Г.', '2026-10-15', '2026-12-15'),
(1604, 'Місія "Відновлення-Схід"', 'Евакуація пошкодженої бронетехніки з переднього краю та відновлення у РВБ', 'підполковник Токар С.М.', '2026-11-01', '2026-12-20');

INSERT INTO Mission_Staff (Name, Role, Mission_ID, Date_Assigned) VALUES
('Ковальов Сергій Павлович', 'Керівник групи оперативного планування J-3', 1601, '2026-08-25'),
('Бондар Дмитро Анатолійович', 'Офіцер координації засобів ППО', 1601, '2026-09-01'),
('Марченко Олексій Юрійович', 'Старший офіцер напрямку логістики J-4', 1602, '2026-09-28'),
('Лисенко Ігор Володимирович', 'Командир зведеного загону БпЛА', 1603, '2026-10-12'),
('Павленко Вадим Ігорович', 'Офіцер взаємодії з артилерією', 1603, '2026-10-14'),
('Карпенко Станіслав Ілліч', 'Начальник евакуаційної групи ОВТ', 1604, '2026-10-29');

-- =========================================================================
-- ВАРІАНТ 17: ЗАБЕЗПЕЧЕННЯ БЕЗПЕКИ (ВСП / Режим та охорона)
-- =========================================================================
CREATE TABLE Security_Tasks (
    Security_Task_ID INT PRIMARY KEY,
    Task_Description VARCHAR(150),
    Risk_Level VARCHAR(50),
    Deadline DATE,
    Assigned_Unit VARCHAR(100)
);

CREATE TABLE Security_Personnel (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Position VARCHAR(100),
    Security_Task_ID INT REFERENCES Security_Tasks(Security_Task_ID),
    Date_Assigned DATE
);

INSERT INTO Security_Tasks VALUES
(1701, 'Охорона та оборона основного командного пункту ОУВ', 'Високий', '2026-12-31', 'Рота охорони КП'),
(1702, 'Контрдиверсійна перевірка у тиловому районі базування', 'Критичний', '2026-11-15', 'Зведена група ВСП'),
(1703, 'Контроль дотримання режиму таємності та маскування ПУ', 'Середній', '2026-11-20', 'Служба охорони держтаємниці');

INSERT INTO Security_Personnel (Name, Position, Security_Task_ID, Date_Assigned) VALUES
('Кравець Олександр Іванович', 'Командир роти охорони КП', 1701, '2025-02-01'),
('Литвиненко Борис Миколайович', 'Старший офіцер відділу ВСП', 1702, '2025-08-15'),
('Гончар Роман Петрович', 'Офіцер режимно-секретного органу', 1703, '2026-01-10');