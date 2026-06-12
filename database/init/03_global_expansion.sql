-- ============================================================
-- AtmosMetrics — 03_global_expansion.sql
-- Expansão global: novas colunas, tabelas e localidades
-- ============================================================

-- Adiciona colunas globais à dim_localidade
ALTER TABLE dim_localidade ADD COLUMN IF NOT EXISTS pais VARCHAR(100) DEFAULT 'Brasil';
ALTER TABLE dim_localidade ADD COLUMN IF NOT EXISTS continente VARCHAR(50) DEFAULT 'América do Sul';
ALTER TABLE dim_localidade ADD COLUMN IF NOT EXISTS latitude_ref DECIMAL(9,6);
ALTER TABLE dim_localidade ADD COLUMN IF NOT EXISTS longitude_ref DECIMAL(9,6);
ALTER TABLE dim_localidade ADD COLUMN IF NOT EXISTS codigo_iso VARCHAR(3);

-- Remove constraint CHECK na coluna regiao (permite regiões globais)
ALTER TABLE dim_localidade DROP CONSTRAINT IF EXISTS dim_localidade_regiao_check;

-- Torna colunas específicas do Brasil opcionais para localidades internacionais
ALTER TABLE dim_localidade ALTER COLUMN uf DROP NOT NULL;
ALTER TABLE dim_localidade ALTER COLUMN estado DROP NOT NULL;
ALTER TABLE dim_localidade ALTER COLUMN regiao DROP NOT NULL;
ALTER TABLE dim_localidade ALTER COLUMN bioma DROP NOT NULL;

-- Atualiza localidades brasileiras existentes com coordenadas e código ISO
UPDATE dim_localidade SET pais = 'Brasil', continente = 'América do Sul', codigo_iso = 'BRA' WHERE pais = 'Brasil' OR pais IS NULL;

-- Índices para consultas globais
CREATE INDEX IF NOT EXISTS idx_localidade_pais ON dim_localidade(pais);
CREATE INDEX IF NOT EXISTS idx_localidade_continente ON dim_localidade(continente);

-- ============================================================
-- NOVA TABELA: fato_qualidade_ar (Qualidade do Ar - OpenWeatherMap)
-- ============================================================
CREATE TABLE IF NOT EXISTS fato_qualidade_ar (
    id_qualidade_ar  BIGSERIAL PRIMARY KEY,
    id_tempo         INT NOT NULL REFERENCES dim_tempo(id_tempo),
    id_localidade    INT NOT NULL REFERENCES dim_localidade(id_localidade),
    aqi              SMALLINT,          -- Índice de Qualidade do Ar (1-5)
    co               DECIMAL(10,2),     -- Monóxido de carbono µg/m³
    no               DECIMAL(10,2),     -- Óxido nítrico µg/m³
    no2              DECIMAL(10,2),     -- Dióxido de nitrogênio µg/m³
    o3               DECIMAL(10,2),     -- Ozônio µg/m³
    so2              DECIMAL(10,2),     -- Dióxido de enxofre µg/m³
    pm2_5            DECIMAL(10,2),     -- Partículas finas µg/m³
    pm10             DECIMAL(10,2),     -- Partículas grossas µg/m³
    nh3              DECIMAL(10,2),     -- Amônia µg/m³
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qualidade_ar_tempo ON fato_qualidade_ar(id_tempo);
CREATE INDEX IF NOT EXISTS idx_qualidade_ar_localidade ON fato_qualidade_ar(id_localidade);

-- ============================================================
-- NOVA TABELA: fato_clima (Dados Climáticos - Open-Meteo)
-- ============================================================
CREATE TABLE IF NOT EXISTS fato_clima (
    id_clima         BIGSERIAL PRIMARY KEY,
    id_tempo         INT NOT NULL REFERENCES dim_tempo(id_tempo),
    id_localidade    INT NOT NULL REFERENCES dim_localidade(id_localidade),
    temperatura_media    DECIMAL(5,2),  -- °C
    temperatura_max      DECIMAL(5,2),  -- °C
    temperatura_min      DECIMAL(5,2),  -- °C
    umidade_media        DECIMAL(5,2),  -- %
    precipitacao_mm      DECIMAL(7,2),  -- mm
    velocidade_vento     DECIMAL(6,2),  -- km/h
    direcao_vento        SMALLINT,      -- graus (0-360)
    pressao_hpa          DECIMAL(7,2),  -- hPa
    radiacao_solar       DECIMAL(8,2),  -- W/m²
    criado_em            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clima_tempo ON fato_clima(id_tempo);
CREATE INDEX IF NOT EXISTS idx_clima_localidade ON fato_clima(id_localidade);

-- ============================================================
-- INSERÇÃO DE LOCALIDADES GLOBAIS DE INTERESSE
-- ============================================================

-- AMÉRICAS
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Washington D.C.', 'Estados Unidos', 'América do Norte', 'USA', 38.9072, -77.0369),
('New York', 'Estados Unidos', 'América do Norte', 'USA', 40.7128, -74.0060),
('Los Angeles', 'Estados Unidos', 'América do Norte', 'USA', 34.0522, -118.2437),
('Chicago', 'Estados Unidos', 'América do Norte', 'USA', 41.8781, -87.6298),
('Houston', 'Estados Unidos', 'América do Norte', 'USA', 29.7604, -95.3698),
('Miami', 'Estados Unidos', 'América do Norte', 'USA', 25.7617, -80.1918),
('Ottawa', 'Canadá', 'América do Norte', 'CAN', 45.4215, -75.6972),
('Toronto', 'Canadá', 'América do Norte', 'CAN', 43.6532, -79.3832),
('Vancouver', 'Canadá', 'América do Norte', 'CAN', 49.2827, -123.1207),
('Montreal', 'Canadá', 'América do Norte', 'CAN', 45.5017, -73.5673)
ON CONFLICT DO NOTHING;

-- EUROPA
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Londres', 'Reino Unido', 'Europa', 'GBR', 51.5074, -0.1278),
('Paris', 'França', 'Europa', 'FRA', 48.8566, 2.3522),
('Berlim', 'Alemanha', 'Europa', 'DEU', 52.5200, 13.4050),
('Madri', 'Espanha', 'Europa', 'ESP', 40.4168, -3.7038),
('Roma', 'Itália', 'Europa', 'ITA', 41.9028, 12.4964),
('Lisboa', 'Portugal', 'Europa', 'PRT', 38.7223, -9.1393),
('Amsterdã', 'Países Baixos', 'Europa', 'NLD', 52.3676, 4.9041),
('Estocolmo', 'Suécia', 'Europa', 'SWE', 59.3293, 18.0686),
('Oslo', 'Noruega', 'Europa', 'NOR', 59.9139, 10.7522),
('Varsóvia', 'Polônia', 'Europa', 'POL', 52.2297, 21.0122),
('Berna', 'Suíça', 'Europa', 'CHE', 46.9480, 7.4474),
('Bruxelas', 'Bélgica', 'Europa', 'BEL', 50.8503, 4.3517),
('Viena', 'Áustria', 'Europa', 'AUT', 48.2082, 16.3738),
('Atenas', 'Grécia', 'Europa', 'GRC', 37.9838, 23.7275),
('Praga', 'República Tcheca', 'Europa', 'CZE', 50.0755, 14.4378)
ON CONFLICT DO NOTHING;

-- ÁFRICA
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Joanesburgo', 'África do Sul', 'África', 'ZAF', -26.2041, 28.0473),
('Lagos', 'Nigéria', 'África', 'NGA', 6.5244, 3.3792),
('Cairo', 'Egito', 'África', 'EGY', 30.0444, 31.2357),
('Nairóbi', 'Quênia', 'África', 'KEN', -1.2921, 36.8219),
('Casablanca', 'Marrocos', 'África', 'MAR', 33.5731, -7.5898),
('Adis Abeba', 'Etiópia', 'África', 'ETH', 9.0250, 38.7469),
('Acra', 'Gana', 'África', 'GHA', 5.6037, -0.1870),
('Dar es Salaam', 'Tanzânia', 'África', 'TZA', -6.7924, 39.2083),
('Kinshasa', 'Rep. Dem. do Congo', 'África', 'COD', -4.4419, 15.2663),
('Luanda', 'Angola', 'África', 'AGO', -8.8390, 13.2894)
ON CONFLICT DO NOTHING;

-- ÁSIA
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Pequim', 'China', 'Ásia', 'CHN', 39.9042, 116.4074),
('Xangai', 'China', 'Ásia', 'CHN', 31.2304, 121.4737),
('Moscou', 'Rússia', 'Europa', 'RUS', 55.7558, 37.6173),
('Novosibirsk', 'Rússia', 'Ásia', 'RUS', 55.0084, 82.9357),
('Yakutsk', 'Rússia', 'Ásia', 'RUS', 62.0355, 129.6755)
ON CONFLICT DO NOTHING;

-- OCEANIA
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Sydney', 'Austrália', 'Oceania', 'AUS', -33.8688, 151.2093),
('Melbourne', 'Austrália', 'Oceania', 'AUS', -37.8136, 144.9631),
('Canberra', 'Austrália', 'Oceania', 'AUS', -35.2809, 149.1300)
ON CONFLICT DO NOTHING;

-- REGIÕES POLARES
INSERT INTO dim_localidade (municipio, pais, continente, codigo_iso, latitude_ref, longitude_ref) VALUES
('Longyearbyen (Svalbard)', 'Noruega', 'Ártico', 'NOR', 78.2232, 15.6267),
('Estação McMurdo', 'Antártica', 'Antártica', 'ATA', -77.8419, 166.6863)
ON CONFLICT DO NOTHING;

-- ============================================================
-- Mensagem de confirmação
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ AtmosMetrics: Expansão global aplicada com sucesso!';
    RAISE NOTICE '   Localidades globais carregadas: %', (SELECT COUNT(*) FROM dim_localidade WHERE pais != 'Brasil');
    RAISE NOTICE '   Tabela fato_qualidade_ar criada';
    RAISE NOTICE '   Tabela fato_clima criada';
END $$;
