DROP TABLE IF EXISTS personnel;
DROP TABLE IF EXISTS units;

CREATE TABLE units (
    unit_id TEXT PRIMARY KEY,
    unit_name TEXT
);

CREATE TABLE personnel (
    id SERIAL PRIMARY KEY,
    name TEXT,
    rank TEXT,
    unit TEXT,
    date_joined DATE
);

INSERT INTO units (unit_id, unit_name) VALUES
('Engineering', 'Інженерний підрозділ'),
('AirDefense', 'Підрозділ ППО');

INSERT INTO personnel (name, rank, unit, date_joined) VALUES
('John Doe', 'Captain', 'Engineering', '2020-05-01'),
('Сергій Коваленко', 'Lieutenant', 'Engineering', '2022-04-12'),
('Іван Мельник', 'Sergeant', 'AirDefense', '2023-09-01');
-- 3. Отримання даних (SELECT)
SELECT name, rank FROM personnel WHERE unit = 'Engineering';

-- 4. Оновлення даних (UPDATE)
UPDATE personnel SET rank = 'Major' WHERE id = 1;

-- 6. Підрахунок кількості (COUNT)
SELECT COUNT(*) FROM personnel;

-- 7. Об'єднання таблиць (JOIN)
SELECT personnel.name, units.unit_name
FROM personnel
JOIN units ON personnel.unit = units.unit_id;

-- 8. Групування за підрозділами (GROUP BY)
SELECT unit, COUNT(*) AS total_personnel
FROM personnel
GROUP BY unit;

-- 9. Сортування за датою (ORDER BY)
SELECT name, date_joined
FROM personnel
ORDER BY date_joined DESC;

-- 10. Підзапит (хто приєднався найпізніше)
SELECT name, date_joined
FROM personnel
WHERE date_joined = (SELECT MAX(date_joined) FROM personnel);