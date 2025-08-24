-- Создание таблиц категорий и условий (уже существующие)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS conditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Новые таблицы для структурированного хранения данных

-- Таблица брендов
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица моделей (связана с брендом)
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, brand_id)
);

-- Таблица цветов
CREATE TABLE IF NOT EXISTS colors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица объемов памяти
CREATE TABLE IF NOT EXISTS storage_capacities (
    id SERIAL PRIMARY KEY,
    capacity_gb INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица рынков/регионов
CREATE TABLE IF NOT EXISTS markets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(100),
    country_code VARCHAR(3), -- ISO код страны
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Обновленная таблица продуктов (без изменений)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    purchase_price NUMERIC(10, 2) NOT NULL,
    sale_price NUMERIC(10, 2),
    quantity INTEGER NOT NULL DEFAULT 1,
    is_sold BOOLEAN NOT NULL DEFAULT FALSE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);

-- Обновленная таблица телефонов с новыми связями
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    purchase_price NUMERIC(10, 2) NOT NULL,
    sale_price NUMERIC(10, 2),
    
    -- Новые поля с foreign keys
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    color_id INTEGER REFERENCES colors(id),
    storage_capacity_id INTEGER REFERENCES storage_capacities(id),
    market_id INTEGER REFERENCES markets(id),
    
    -- Существующие поля
    condition_id INTEGER REFERENCES conditions(id),
    is_sold BOOLEAN NOT NULL DEFAULT FALSE,
    battery_health INTEGER,
    repaired BOOLEAN,
    full_kit BOOLEAN,
    
    -- Дополнительные поля
    imei VARCHAR(17), -- IMEI номер
    serial_number VARCHAR(50), -- Серийный номер
    purchase_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица транзакций (без изменений)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER REFERENCES phones(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Вставка базовых данных

-- Категории
INSERT INTO categories (name) VALUES ('Телефоны') ON CONFLICT (name) DO NOTHING;
INSERT INTO categories (name) VALUES ('Аксессуары') ON CONFLICT (name) DO NOTHING;

-- Условия
INSERT INTO conditions (name) VALUES ('Новое') ON CONFLICT (name) DO NOTHING;
INSERT INTO conditions (name) VALUES ('Б/У') ON CONFLICT (name) DO NOTHING;

-- Бренды
INSERT INTO brands (name) VALUES ('Apple') ON CONFLICT (name) DO NOTHING;
INSERT INTO brands (name) VALUES ('Samsung') ON CONFLICT (name) DO NOTHING;
INSERT INTO brands (name) VALUES ('Xiaomi') ON CONFLICT (name) DO NOTHING;
INSERT INTO brands (name) VALUES ('Huawei') ON CONFLICT (name) DO NOTHING;
INSERT INTO brands (name) VALUES ('Google') ON CONFLICT (name) DO NOTHING;
INSERT INTO brands (name) VALUES ('OnePlus') ON CONFLICT (name) DO NOTHING;

-- Модели iPhone (примеры)
INSERT INTO models (name, brand_id) 
SELECT 'iPhone 15 Pro Max', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 15 Pro', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 15', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 14 Pro Max', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 14 Pro', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 14', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 13 Pro Max', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 13 Pro', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'iPhone 13', id FROM brands WHERE name = 'Apple' 
ON CONFLICT (name, brand_id) DO NOTHING;

-- Модели Samsung (примеры)
INSERT INTO models (name, brand_id) 
SELECT 'Galaxy S24 Ultra', id FROM brands WHERE name = 'Samsung' 
ON CONFLICT (name, brand_id) DO NOTHING;

INSERT INTO models (name, brand_id) 
SELECT 'Galaxy S23 Ultra', id FROM brands WHERE name = 'Samsung' 
ON CONFLICT (name, brand_id) DO NOTHING;

-- Цвета
INSERT INTO colors (name) VALUES ('Черный') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Белый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Синий') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Розовый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Фиолетовый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Красный') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Желтый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Зеленый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Серебристый') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Золотой') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Space Gray') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Midnight') ON CONFLICT (name) DO NOTHING;
INSERT INTO colors (name) VALUES ('Starlight') ON CONFLICT (name) DO NOTHING;

-- Объемы памяти iPhone
INSERT INTO storage_capacities (capacity_gb) VALUES (64) ON CONFLICT (capacity_gb) DO NOTHING;
INSERT INTO storage_capacities (capacity_gb) VALUES (128) ON CONFLICT (capacity_gb) DO NOTHING;
INSERT INTO storage_capacities (capacity_gb) VALUES (256) ON CONFLICT (capacity_gb) DO NOTHING;
INSERT INTO storage_capacities (capacity_gb) VALUES (512) ON CONFLICT (capacity_gb) DO NOTHING;
INSERT INTO storage_capacities (capacity_gb) VALUES (1024) ON CONFLICT (capacity_gb) DO NOTHING;

-- Рынки
INSERT INTO markets (name, region, country_code) VALUES ('США', 'Америка', 'US') ON CONFLICT (name) DO NOTHING;
INSERT INTO markets (name, region, country_code) VALUES ('Европа', 'Европа', 'EU') ON CONFLICT (name) DO NOTHING;
INSERT INTO markets (name, region, country_code) VALUES ('Китай', 'Азия', 'CN') ON CONFLICT (name) DO NOTHING;

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_phones_model_id ON phones(model_id);
CREATE INDEX IF NOT EXISTS idx_phones_color_id ON phones(color_id);
CREATE INDEX IF NOT EXISTS idx_phones_storage_id ON phones(storage_capacity_id);
CREATE INDEX IF NOT EXISTS idx_phones_market_id ON phones(market_id);
CREATE INDEX IF NOT EXISTS idx_phones_condition_id ON phones(condition_id);
CREATE INDEX IF NOT EXISTS idx_phones_is_sold ON phones(is_sold);
CREATE INDEX IF NOT EXISTS idx_models_brand_id ON models(brand_id);
CREATE INDEX IF NOT EXISTS idx_transactions_phone_id ON transactions(phone_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);