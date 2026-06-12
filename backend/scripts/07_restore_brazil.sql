-- ============================================================
-- AtmosMetrics — Restauração do Brasil (Média Granularidade)
-- ============================================================

-- Insere as 27 capitais do Brasil para que elas representem seus respectivos estados,
-- garantindo alta performance no mapa sem congelar o navegador.

INSERT INTO dim_localidade (municipio, estado, uf, regiao, pais, continente, latitude_ref, longitude_ref)
VALUES
('São Paulo', 'São Paulo', 'SP', 'Sudeste', 'Brasil', 'América do Sul', -23.5505, -46.6333),
('Rio de Janeiro', 'Rio de Janeiro', 'RJ', 'Sudeste', 'Brasil', 'América do Sul', -22.9068, -43.1729),
('Belo Horizonte', 'Minas Gerais', 'MG', 'Sudeste', 'Brasil', 'América do Sul', -19.9167, -43.9345),
('Vitória', 'Espírito Santo', 'ES', 'Sudeste', 'Brasil', 'América do Sul', -20.3155, -40.3128),
('Brasília', 'Distrito Federal', 'DF', 'Centro-Oeste', 'Brasil', 'América do Sul', -15.7942, -47.8822),
('Goiânia', 'Goiás', 'GO', 'Centro-Oeste', 'Brasil', 'América do Sul', -16.6869, -49.2648),
('Cuiabá', 'Mato Grosso', 'MT', 'Centro-Oeste', 'Brasil', 'América do Sul', -15.6010, -56.0974),
('Campo Grande', 'Mato Grosso do Sul', 'MS', 'Centro-Oeste', 'Brasil', 'América do Sul', -20.4428, -54.6464),
('Curitiba', 'Paraná', 'PR', 'Sul', 'Brasil', 'América do Sul', -25.4290, -49.2671),
('Florianópolis', 'Santa Catarina', 'SC', 'Sul', 'Brasil', 'América do Sul', -27.5954, -48.5480),
('Porto Alegre', 'Rio Grande do Sul', 'RS', 'Sul', 'Brasil', 'América do Sul', -30.0346, -51.2177),
('Salvador', 'Bahia', 'BA', 'Nordeste', 'Brasil', 'América do Sul', -12.9714, -38.5014),
('Recife', 'Pernambuco', 'PE', 'Nordeste', 'Brasil', 'América do Sul', -8.0476, -34.8770),
('Fortaleza', 'Ceará', 'CE', 'Nordeste', 'Brasil', 'América do Sul', -3.7172, -38.5433),
('Maceió', 'Alagoas', 'AL', 'Nordeste', 'Brasil', 'América do Sul', -9.6662, -35.7351),
('Natal', 'Rio Grande do Norte', 'RN', 'Nordeste', 'Brasil', 'América do Sul', -5.7945, -35.2110),
('João Pessoa', 'Paraíba', 'PB', 'Nordeste', 'Brasil', 'América do Sul', -7.1195, -34.8450),
('Aracaju', 'Sergipe', 'SE', 'Nordeste', 'Brasil', 'América do Sul', -10.9472, -37.0731),
('São Luís', 'Maranhão', 'MA', 'Nordeste', 'Brasil', 'América do Sul', -2.5307, -44.3068),
('Teresina', 'Piauí', 'PI', 'Nordeste', 'Brasil', 'América do Sul', -5.0892, -42.8016),
('Manaus', 'Amazonas', 'AM', 'Norte', 'Brasil', 'América do Sul', -3.1190, -60.0217),
('Belém', 'Pará', 'PA', 'Norte', 'Brasil', 'América do Sul', -1.4550, -48.5024),
('Macapá', 'Amapá', 'AP', 'Norte', 'Brasil', 'América do Sul', 0.0389, -51.0556),
('Boa Vista', 'Roraima', 'RR', 'Norte', 'Brasil', 'América do Sul', 2.8235, -60.6758),
('Porto Velho', 'Rondônia', 'RO', 'Norte', 'Brasil', 'América do Sul', -8.7612, -63.9039),
('Rio Branco', 'Acre', 'AC', 'Norte', 'Brasil', 'América do Sul', -9.9750, -67.8249),
('Palmas', 'Tocantins', 'TO', 'Norte', 'Brasil', 'América do Sul', -10.2491, -48.3243)
ON CONFLICT DO NOTHING;
