CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS conditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    purchase_price NUMERIC(10, 2) NOT NULL,
    sale_price NUMERIC(10, 2),
    quantity INTEGER NOT NULL DEFAULT 1, -- <-- Новое поле
    color VARCHAR(100),
    condition_id INTEGER REFERENCES conditions(id),
    is_sold BOOLEAN NOT NULL DEFAULT FALSE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    purchase_price NUMERIC(10, 2) NOT NULL,
    sale_price NUMERIC(10, 2),
    color VARCHAR(100),
    condition_id INTEGER REFERENCES conditions(id),
    is_sold BOOLEAN NOT NULL DEFAULT FALSE,
    battery_health INTEGER,
    repaired BOOLEAN,
    full_kit BOOLEAN
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    phone_id INTEGER REFERENCES phones(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO categories (name) VALUES ('Телефоны') ON CONFLICT (name) DO NOTHING;
INSERT INTO categories (name) VALUES ('Аксессуары') ON CONFLICT (name) DO NOTHING;
INSERT INTO conditions (name) VALUES ('Новое') ON CONFLICT (name) DO NOTHING;
INSERT INTO conditions (name) VALUES ('Б/У') ON CONFLICT (name) DO NOTHING;