-- Rijnland Peilgebieden Schema
-- Voor Hoogheemraadschap van Rijnland

-- Peilgebieden table (water level areas)
CREATE TABLE IF NOT EXISTS peilbesluiten.peilgebieden_rijnland (
    id SERIAL PRIMARY KEY,
    oracle_objectid VARCHAR(50),
    code VARCHAR(100),
    naam VARCHAR(255),
    statusobject VARCHAR(100),
    soortpeilgebied VARCHAR(100),
    soortafwatering VARCHAR(100),
    peilbeherendeinstantie VARCHAR(100),
    peilindexering VARCHAR(100),
    jaartalhuidigpeil VARCHAR(50),
    jaartalvolgendewijziging VARCHAR(50),
    eindzomerpeil DOUBLE PRECISION,
    eindwinterpeil DOUBLE PRECISION,
    vorigzomerpeil DOUBLE PRECISION,
    vorigwinterpeil DOUBLE PRECISION,
    oppervlakte DOUBLE PRECISION,
    omtrek DOUBLE PRECISION,
    opmerking TEXT,
    hyperlink TEXT,
    soortpeilbeheer VARCHAR(100),
    vastpeil DOUBLE PRECISION,
    zomerpeil DOUBLE PRECISION,
    winterpeil DOUBLE PRECISION,
    flexzomerpeilondergrens DOUBLE PRECISION,
    flexzomerpeilbovengrens DOUBLE PRECISION,
    flexwinterpeilondergrens DOUBLE PRECISION,
    flexwinterpeilbovengrens DOUBLE PRECISION,
    zomerpeiltekst VARCHAR(50),
    winterpeiltekst VARCHAR(50),
    verlengdtot VARCHAR(50),
    geometry GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index for geometry
CREATE INDEX IF NOT EXISTS idx_peilgebieden_rijnland_geometry
    ON peilbesluiten.peilgebieden_rijnland USING GIST (geometry);

-- Create index on code for quick lookups
CREATE INDEX IF NOT EXISTS idx_peilgebieden_rijnland_code
    ON peilbesluiten.peilgebieden_rijnland (code);

-- Create index on name
CREATE INDEX IF NOT EXISTS idx_peilgebieden_rijnland_naam
    ON peilbesluiten.peilgebieden_rijnland (naam);

-- Trigger to automatically update updated_at
CREATE TRIGGER update_peilgebieden_rijnland_updated_at
    BEFORE UPDATE ON peilbesluiten.peilgebieden_rijnland
    FOR EACH ROW
    EXECUTE FUNCTION peilbesluiten.update_updated_at_column();

-- View for easy querying
CREATE OR REPLACE VIEW peilbesluiten.peilgebieden_rijnland_view AS
SELECT
    id,
    code,
    naam,
    statusobject,
    soortpeilgebied,
    soortafwatering,
    peilbeherendeinstantie,
    hyperlink as besluit_url,
    soortpeilbeheer,
    zomerpeil,
    winterpeil,
    oppervlakte,
    ST_AsGeoJSON(geometry) as geojson,
    ST_Area(geometry::geography) / 10000 as oppervlakte_ha,
    created_at,
    updated_at
FROM peilbesluiten.peilgebieden_rijnland;

COMMENT ON TABLE peilbesluiten.peilgebieden_rijnland IS 'Peilgebieden van Hoogheemraadschap van Rijnland';
COMMENT ON COLUMN peilbesluiten.peilgebieden_rijnland.code IS 'Unieke code van het peilgebied';
COMMENT ON COLUMN peilbesluiten.peilgebieden_rijnland.naam IS 'Naam van het peilgebied';
COMMENT ON COLUMN peilbesluiten.peilgebieden_rijnland.zomerpeil IS 'Zomerpeil in meters NAP';
COMMENT ON COLUMN peilbesluiten.peilgebieden_rijnland.winterpeil IS 'Winterpeil in meters NAP';
COMMENT ON COLUMN peilbesluiten.peilgebieden_rijnland.hyperlink IS 'URL naar het peilbesluit op officielebekendmakingen.nl';
