-- ============================================================
-- AtmosMetrics — Mock de Qualidade do Ar
-- Preenche as localidades com valores randômicos realistas de AQI
-- para fins de testes visuais no Front-End
-- ============================================================

DO $$
DECLARE
    id_tempo_hoje INTEGER;
    loc RECORD;
    rand_aqi INTEGER;
    rand_pm25 DECIMAL;
    rand_pm10 DECIMAL;
    rand_co DECIMAL;
    rand_o3 DECIMAL;
BEGIN
    -- 1. Garante que existe a dimensão tempo de hoje
    SELECT id_tempo INTO id_tempo_hoje 
    FROM dim_tempo 
    WHERE data_completa = CURRENT_DATE;

    IF id_tempo_hoje IS NULL THEN
        INSERT INTO dim_tempo (
            data_completa, ano, semestre, trimestre, mes, nome_mes, semana_do_ano, dia, dia_da_semana, nome_dia, e_fim_de_semana
        )
        VALUES (
            CURRENT_DATE,
            EXTRACT(YEAR FROM CURRENT_DATE),
            CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN 1 ELSE 2 END,
            EXTRACT(QUARTER FROM CURRENT_DATE),
            EXTRACT(MONTH FROM CURRENT_DATE),
            to_char(CURRENT_DATE, 'Month'),
            EXTRACT(WEEK FROM CURRENT_DATE),
            EXTRACT(DAY FROM CURRENT_DATE),
            EXTRACT(DOW FROM CURRENT_DATE),
            to_char(CURRENT_DATE, 'Day'),
            EXTRACT(ISODOW FROM CURRENT_DATE) IN (6, 7)
        ) RETURNING id_tempo INTO id_tempo_hoje;
    END IF;

    -- 2. Itera sobre todas as localidades que tem coordenadas e insere medições aleatórias
    FOR loc IN 
        SELECT id_localidade, pais, continente 
        FROM dim_localidade 
        WHERE latitude_ref IS NOT NULL
    LOOP
        -- Se já existe para essa data/localidade, pula
        IF EXISTS (
            SELECT 1 FROM fato_qualidade_ar 
            WHERE id_tempo = id_tempo_hoje AND id_localidade = loc.id_localidade
        ) THEN
            CONTINUE;
        END IF;

        -- Gera AQI randômico simulando a realidade de cada continente/país
        IF loc.pais = 'China' OR loc.pais = 'India' OR loc.pais = 'Bangladesh' THEN
            -- Mais poluição na Ásia
            rand_aqi := floor(random() * (400 - 150 + 1) + 150);
        ELSIF loc.pais = 'Brasil' AND random() > 0.8 THEN
            -- Queimadas esporádicas no BR
            rand_aqi := floor(random() * (300 - 120 + 1) + 120);
        ELSIF loc.continente = 'Europe' OR loc.continente = 'North America' THEN
            -- Ar mais limpo
            rand_aqi := floor(random() * (100 - 10 + 1) + 10);
        ELSE
            -- Padrão global aleatório
            rand_aqi := floor(random() * (200 - 20 + 1) + 20);
        END IF;

        -- Variáveis proporcionais ao AQI
        rand_pm25 := (rand_aqi * random() * 0.8)::DECIMAL(10,2);
        rand_pm10 := (rand_aqi * random() * 1.5)::DECIMAL(10,2);
        rand_co := (rand_aqi * random() * 10)::DECIMAL(10,2);
        rand_o3 := (rand_aqi * random() * 0.5)::DECIMAL(10,2);

        INSERT INTO fato_qualidade_ar (
            id_tempo,
            id_localidade,
            aqi,
            co,
            no,
            no2,
            o3,
            so2,
            pm2_5,
            pm10,
            nh3
        ) VALUES (
            id_tempo_hoje,
            loc.id_localidade,
            rand_aqi,
            rand_co,
            (random() * 5)::DECIMAL(10,2),
            (random() * 10)::DECIMAL(10,2),
            rand_o3,
            (random() * 8)::DECIMAL(10,2),
            rand_pm25,
            rand_pm10,
            (random() * 2)::DECIMAL(10,2)
        );
    END LOOP;

END $$;
