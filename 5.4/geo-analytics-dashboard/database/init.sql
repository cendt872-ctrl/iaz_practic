CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
DROP TABLE IF EXISTS object_status_history CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS resources CASCADE;
DROP TABLE IF EXISTS objects CASCADE;
DROP TABLE IF EXISTS areas CASCADE;
DROP TABLE IF EXISTS osm_features CASCADE;
CREATE TABLE osm_features (
    osm_id BIGINT PRIMARY KEY,
    osm_type VARCHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    geom GEOMETRY(Geometry, 4326) NOT NULL,
    tags JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_osm_features_geom ON osm_features USING GIST (geom);
CREATE TABLE areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    area_type VARCHAR(64) NOT NULL,
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    area_sq_km NUMERIC(12, 2) NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_areas_geom ON areas USING GIST (geom);
CREATE TABLE objects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    object_type VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    code VARCHAR(64) NOT NULL UNIQUE,
    sidc VARCHAR(30) NOT NULL,
    affiliation VARCHAR(32) NOT NULL DEFAULT 'friendly',
    echelon VARCHAR(32) NOT NULL DEFAULT 'company',
    status VARCHAR(32) NOT NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    osm_feature_id BIGINT REFERENCES osm_features(osm_id) ON DELETE SET NULL,
    area_id INTEGER REFERENCES areas(id) ON DELETE SET NULL,
    attributes JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_objects_geom ON objects USING GIST (geom);
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(220) NOT NULL,
    category VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    object_id INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_events_geom ON events USING GIST (geom);
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    category VARCHAR(64) NOT NULL,
    total_amount INTEGER NOT NULL,
    available_amount INTEGER NOT NULL,
    in_use_amount INTEGER NOT NULL,
    unit VARCHAR(32) NOT NULL DEFAULT 'од.',
    condition VARCHAR(32) NOT NULL,
    object_id INTEGER REFERENCES objects(id) ON DELETE SET NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_resources_geom ON resources USING GIST (geom);
CREATE TABLE object_status_history (
    id SERIAL PRIMARY KEY,
    object_id INTEGER NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
    previous_status VARCHAR(32) NOT NULL,
    new_status VARCHAR(32) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL,
    reason VARCHAR(255) NOT NULL,
    is_synthetic BOOLEAN NOT NULL DEFAULT TRUE
);
INSERT INTO osm_features (osm_id, osm_type, name, category, geom, tags, is_synthetic) VALUES
(26150422, 'node', 'Кропивницький', 'city', ST_SetSRID(ST_MakePoint(32.2623, 48.5079), 4326), '{}'::jsonb, FALSE),
(25870505, 'node', 'Черкаси', 'city', ST_SetSRID(ST_MakePoint(32.0588, 49.4444), 4326), '{}'::jsonb, FALSE),
(26150198, 'node', 'Вінниця', 'city', ST_SetSRID(ST_MakePoint(28.4682, 49.2331), 4326), '{}'::jsonb, FALSE),
(26150301, 'node', 'Полтава', 'city', ST_SetSRID(ST_MakePoint(34.5514, 49.5883), 4326), '{}'::jsonb, FALSE),
(31490011, 'node', 'Умань', 'town', ST_SetSRID(ST_MakePoint(30.2218, 48.7484), 4326), '{}'::jsonb, FALSE),
(31490012, 'node', 'Олександрія', 'town', ST_SetSRID(ST_MakePoint(33.1169, 48.6696), 4326), '{}'::jsonb, FALSE),
(40100201, 'way', 'Автошлях М-30', 'highway', ST_GeomFromText('LINESTRING(28.4682 49.2331, 30.2218 48.7484, 32.2623 48.5079, 33.1169 48.6696)', 4326), '{}'::jsonb, FALSE);
INSERT INTO areas (name, area_type, geom, area_sq_km, attributes, is_synthetic) VALUES
('Сектор Центр-Північ', 'monitoring_zone', ST_GeomFromText('POLYGON((29.50 49.90, 32.20 49.90, 32.20 48.80, 29.50 48.80, 29.50 49.90))', 4326), 26450.00, '{}'::jsonb, TRUE),
('Сектор Інгул', 'logistics_sector', ST_GeomFromText('POLYGON((31.20 48.80, 33.60 48.80, 33.60 47.80, 31.20 47.80, 31.20 48.80))', 4326), 19820.00, '{}'::jsonb, TRUE);
DO $$
DECLARE
    i INT;
    types_arr VARCHAR[] := ARRAY['command_post', 'mechanized_unit', 'air_defense', 'logistics_hub', 'comms_node', 'radar_station'];
    cats_arr VARCHAR[] := ARRAY['Сухопутні війська', 'Повітряні Сили', 'Військово-Морські Сили', 'Десантно-штурмові війська', 'Сили спеціальних операцій', 'Сили територіальної оборони', 'Морська піхота', 'Військова служба правопорядку'];
    sidc_arr VARCHAR[] := ARRAY['SFGPE-----F----', 'SFGPUCI---F----', 'SFGPUCD---F----', 'SFGPUSS---F----', 'SFGPUSM---F----', 'SFGPUCF---F----'];
    status_arr VARCHAR[] := ARRAY['active', 'active', 'standby', 'maintenance', 'relocating'];
    osm_ids BIGINT[] := ARRAY[26150422, 25870505, 26150198, 26150301, 31490011, 31490012];
BEGIN
    FOR i IN 1..75 LOOP
        INSERT INTO objects (name, object_type, category, code, sidc, affiliation, echelon, status, geom, osm_feature_id, area_id, attributes, is_synthetic)
        VALUES (
            'Умовний об''єкт #' || LPAD(i::text, 3, '0'),
            types_arr[1 + (i % 6)],
            cats_arr[1 + (i % 8)],
            'UAF-SYN-' || LPAD(i::text, 4, '0'),
            sidc_arr[1 + (i % 6)],
            'friendly', 'company',
            status_arr[1 + (i % 5)],
            ST_SetSRID(ST_MakePoint(28.2 + ((i * 37) % 650) / 100.0, 47.8 + ((i * 53) % 240) / 100.0), 4326),
            osm_ids[1 + (i % 6)],
            1 + (i % 2),
            jsonb_build_object('readiness_pct', 75 + (i % 25)),
            TRUE
        );
    END LOOP;
    FOR i IN 1..150 LOOP
        INSERT INTO events (title, category, severity, status, event_time, geom, object_id, description, is_synthetic)
        VALUES (
            'Подія моніторингу #' || LPAD(i::text, 4, '0'),
            (ARRAY['Телеметрія', 'Логістика', 'Зв''язок', 'Інженерний моніторинг'])[1 + (i % 4)],
            (ARRAY['low', 'medium', 'high', 'critical'])[1 + (i % 4)],
            (ARRAY['open', 'in_progress', 'resolved'])[1 + (i % 3)],
            NOW() - ((i % 32) || ' days')::interval,
            ST_SetSRID(ST_MakePoint(28.5 + ((i * 29) % 600) / 100.0, 48.0 + ((i * 41) % 210) / 100.0), 4326),
            1 + (i % 75),
            'Синтетичне повідомлення телеметрії та контролю стану.',
            TRUE
        );
    END LOOP;
    FOR i IN 1..40 LOOP
        INSERT INTO resources (name, category, total_amount, available_amount, in_use_amount, unit, condition, object_id, geom, is_synthetic)
        VALUES (
            'Ресурсний пакет #' || i,
            (ARRAY['Пально-мастильні матеріали', 'Енергозабезпечення', 'Засоби зв''язку', 'Медичне майно'])[1 + (i % 4)],
            200 + (i * 10), 120 + (i * 5), 80 + (i * 5), 'од.', 'nominal', 1 + (i % 75),
            ST_SetSRID(ST_MakePoint(30.5, 48.6), 4326), TRUE
        );
    END LOOP;
    FOR i IN 1..180 LOOP
        INSERT INTO object_status_history (object_id, previous_status, new_status, changed_at, reason, is_synthetic)
        VALUES (1 + (i % 75), 'standby', 'active', NOW() - ((i % 32) || ' days')::interval, 'Планова ротація режиму #' || i, TRUE);
    END LOOP;
END $$;