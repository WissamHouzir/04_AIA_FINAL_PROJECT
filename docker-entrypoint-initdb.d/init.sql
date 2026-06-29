CREATE TABLE IF NOT EXISTS climate_news_data (
    id SERIAL PRIMARY KEY,
    text TEXT,
    label VARCHAR(255),
    pred_label VARCHAR(255),
    created_at TIMESTAMP,
    is_true INTEGER,
    is_fake INTEGER,
    is_biased INTEGER
);