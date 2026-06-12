-- ============================================================
-- AtmosMetrics — Adição de Estados Globais (Resolução Assimétrica)
-- ============================================================

-- Adiciona estados/províncias principais de alguns países, utilizando a capital 
-- ou cidade principal do estado como representante no campo 'municipio'

INSERT INTO dim_localidade (municipio, estado, regiao, pais, continente, latitude_ref, longitude_ref)
VALUES
-- Austrália
('Sydney', 'New South Wales', 'Oceania', 'Austrália', 'Oceania', -33.8688, 151.2093),
('Melbourne', 'Victoria', 'Oceania', 'Austrália', 'Oceania', -37.8136, 144.9631),
('Brisbane', 'Queensland', 'Oceania', 'Austrália', 'Oceania', -27.4705, 153.0260),
('Perth', 'Western Australia', 'Oceania', 'Austrália', 'Oceania', -31.9505, 115.8605),
('Adelaide', 'South Australia', 'Oceania', 'Austrália', 'Oceania', -34.9285, 138.6007),

-- Alemanha
('Berlim', 'Berlim', 'Europa Central', 'Alemanha', 'Europa', 52.5200, 13.4050),
('Munique', 'Baviera', 'Europa Central', 'Alemanha', 'Europa', 48.1351, 11.5820),
('Frankfurt', 'Hesse', 'Europa Central', 'Alemanha', 'Europa', 50.1109, 8.6821),
('Hamburgo', 'Hamburgo', 'Europa Central', 'Alemanha', 'Europa', 53.5511, 9.9937),

-- África do Sul
('Cidade do Cabo', 'Western Cape', 'África Austral', 'África do Sul', 'África', -33.9249, 18.4241),
('Joanesburgo', 'Gauteng', 'África Austral', 'África do Sul', 'África', -26.2041, 28.0473),
('Durban', 'KwaZulu-Natal', 'África Austral', 'África do Sul', 'África', -29.8587, 31.0218),

-- Índia
('Mumbai', 'Maharashtra', 'Sul da Ásia', 'Índia', 'Ásia', 19.0760, 72.8777),
('Délhi', 'Délhi', 'Sul da Ásia', 'Índia', 'Ásia', 28.7041, 77.1025),
('Bangalore', 'Karnataka', 'Sul da Ásia', 'Índia', 'Ásia', 12.9716, 77.5946),
('Calcutá', 'Bengala Ocidental', 'Sul da Ásia', 'Índia', 'Ásia', 22.5726, 88.3639),

-- China
('Pequim', 'Pequim', 'Leste da Ásia', 'China', 'Ásia', 39.9042, 116.4074),
('Xangai', 'Xangai', 'Leste da Ásia', 'China', 'Ásia', 31.2304, 121.4737),
('Guangzhou', 'Guangdong', 'Leste da Ásia', 'China', 'Ásia', 23.1291, 113.2644),
('Shenzhen', 'Guangdong', 'Leste da Ásia', 'China', 'Ásia', 22.5431, 114.0579),

-- EUA
('Los Angeles', 'California', 'América do Norte', 'EUA', 'América do Norte', 34.0522, -118.2437),
('Nova York', 'New York', 'América do Norte', 'EUA', 'América do Norte', 40.7128, -74.0060),
('Houston', 'Texas', 'América do Norte', 'EUA', 'América do Norte', 29.7604, -95.3698),
('Miami', 'Flórida', 'América do Norte', 'EUA', 'América do Norte', 25.7617, -80.1918),
('Chicago', 'Illinois', 'América do Norte', 'EUA', 'América do Norte', 41.8781, -87.6298),
('Seattle', 'Washington', 'América do Norte', 'EUA', 'América do Norte', 47.6062, -122.3321),
('Denver', 'Colorado', 'América do Norte', 'EUA', 'América do Norte', 39.7392, -104.9903),

-- Canadá
('Toronto', 'Ontario', 'América do Norte', 'Canadá', 'América do Norte', 43.651070, -79.347015),
('Vancouver', 'British Columbia', 'América do Norte', 'Canadá', 'América do Norte', 49.2827, -123.1207),
('Montreal', 'Quebec', 'América do Norte', 'Canadá', 'América do Norte', 45.5017, -73.5673),

-- América do Sul
('Buenos Aires', 'Buenos Aires', 'Cone Sul', 'Argentina', 'América do Sul', -34.6037, -58.3816),
('Córdoba', 'Córdoba', 'Cone Sul', 'Argentina', 'América do Sul', -31.4201, -64.1888),
('Santiago', 'Região Metropolitana', 'Cone Sul', 'Chile', 'América do Sul', -33.4489, -70.6693),
('Bogotá', 'Bogotá', 'Região Andina', 'Colômbia', 'América do Sul', 4.7110, -74.0721),
('Lima', 'Lima', 'Região Andina', 'Peru', 'América do Sul', -12.0464, -77.0428),

-- Europa (Além da Alemanha)
('Londres', 'Inglaterra', 'Europa Ocidental', 'Reino Unido', 'Europa', 51.5074, -0.1278),
('Paris', 'Île-de-France', 'Europa Ocidental', 'França', 'Europa', 48.8566, 2.3522),
('Lyon', 'Auvergne-Rhône-Alpes', 'Europa Ocidental', 'França', 'Europa', 45.7640, 4.8357),
('Roma', 'Lácio', 'Europa Meridional', 'Itália', 'Europa', 41.9028, 12.4964),
('Milão', 'Lombardia', 'Europa Meridional', 'Itália', 'Europa', 45.4642, 9.1900),
('Madri', 'Comunidade de Madrid', 'Europa Meridional', 'Espanha', 'Europa', 40.4168, -3.7038),
('Barcelona', 'Catalunha', 'Europa Meridional', 'Espanha', 'Europa', 41.3851, 2.1734),

-- Ásia (Japão e Coreia)
('Tóquio', 'Tóquio', 'Leste da Ásia', 'Japão', 'Ásia', 35.6762, 139.6503),
('Osaka', 'Osaka', 'Leste da Ásia', 'Japão', 'Ásia', 34.6937, 135.5023),
('Seul', 'Área da Capital', 'Leste da Ásia', 'Coreia do Sul', 'Ásia', 37.5665, 126.9780)
ON CONFLICT (codigo_ibge) DO NOTHING;
