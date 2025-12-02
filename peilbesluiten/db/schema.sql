-- Peilbesluiten Database Schema
-- Voor Hoogheemraadschap De Stichtse Rijnlanden (HDSR)

-- Enable PostGIS extension for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create schema for peilbesluiten
CREATE SCHEMA IF NOT EXISTS peilbesluiten;

-- Peilbesluiten table (water level decisions)
CREATE TABLE IF NOT EXISTS peilbesluiten.peilbesluiten (
    id SERIAL PRIMARY KEY,
    objectid INTEGER UNIQUE NOT NULL,
    ws_pbnaam VARCHAR(255) NOT NULL,  -- Peilbesluit naam
    ws_gpnaam VARCHAR(255),            -- Gebiedsplan naam
    ws_info TEXT,                      -- Link naar besluit op overheid.nl
    ws_dtm_goed TIMESTAMP,             -- Datum goedkeuring
    globalid UUID UNIQUE,
    geometry GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index for geometry
CREATE INDEX IF NOT EXISTS idx_peilbesluiten_geometry
    ON peilbesluiten.peilbesluiten USING GIST (geometry);

-- Create index on name for quick lookups
CREATE INDEX IF NOT EXISTS idx_peilbesluiten_naam
    ON peilbesluiten.peilbesluiten (ws_pbnaam);

-- Create index on approval date
CREATE INDEX IF NOT EXISTS idx_peilbesluiten_datum
    ON peilbesluiten.peilbesluiten (ws_dtm_goed);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION peilbesluiten.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_peilbesluiten_updated_at
    BEFORE UPDATE ON peilbesluiten.peilbesluiten
    FOR EACH ROW
    EXECUTE FUNCTION peilbesluiten.update_updated_at_column();

-- View for easy querying with human-readable geometry
CREATE OR REPLACE VIEW peilbesluiten.peilbesluiten_view AS
SELECT
    id,
    objectid,
    ws_pbnaam as naam,
    ws_gpnaam as gebiedsplan,
    ws_info as besluit_url,
    ws_dtm_goed as goedkeuringsdatum,
    ST_AsGeoJSON(geometry) as geojson,
    ST_Area(geometry::geography) / 10000 as oppervlakte_ha,
    created_at,
    updated_at
FROM peilbesluiten.peilbesluiten;

COMMENT ON TABLE peilbesluiten.peilbesluiten IS 'Peilbesluiten van Hoogheemraadschap De Stichtse Rijnlanden';
COMMENT ON COLUMN peilbesluiten.peilbesluiten.ws_pbnaam IS 'Naam van het peilbesluit';
COMMENT ON COLUMN peilbesluiten.peilbesluiten.ws_gpnaam IS 'Naam van het gebiedsplan';
COMMENT ON COLUMN peilbesluiten.peilbesluiten.ws_info IS 'URL naar het besluit op lokaleregelgeving.overheid.nl';
COMMENT ON COLUMN peilbesluiten.peilbesluiten.ws_dtm_goed IS 'Datum van goedkeuring van het peilbesluit';
