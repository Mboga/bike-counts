-- File: db_init/init.sql
-- This script runs automatically when the PostgreSQL container starts for the first time.
-- It ensures the 'cleaned_data' table exists before your Python script tries to write to it.
-- File: db_init/init.sql
CREATE TABLE IF NOT EXISTS cleaned_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    device_name VARCHAR(255), -- Matches df_cleaned output
    count BIGINT,             -- Matches df_cleaned output
    average_speed DOUBLE PRECISION, -- Matches df_cleaned output
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    easting DOUBLE PRECISION,
    northing DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);