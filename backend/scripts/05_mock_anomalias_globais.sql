-- ============================================================
-- AtmosMetrics — Mock de Anomalias/Clima Global
-- ============================================================

-- Gera temperaturas extremas (ondas de calor ou nevascas) para os
-- novos estados globais inseridos (China, Austrália, EUA, etc)
-- e capitais do Brasil, de forma que o Dashboard Principal seja preenchido.
-- O algoritmo é ciente das estações do ano e regiões geográficas.

DO $$
DECLARE
    loc_record RECORD;
    v_id_tempo INTEGER;
    v_temp_max NUMERIC;
    v_temp_min NUMERIC;
    v_temp_med NUMERIC;
    v_month INTEGER;
    v_sin_seasonal NUMERIC;
    v_amp NUMERIC;
BEGIN
    -- 1. Pegar o ID do tempo atual
    SELECT id_tempo INTO v_id_tempo 
    FROM dim_tempo 
    WHERE data_completa = CURRENT_DATE;

    IF v_id_tempo IS NULL THEN
        INSERT INTO dim_tempo (
            data_completa, ano, semestre, trimestre, mes, nome_mes, semana_do_ano, dia, dia_da_semana, nome_dia, e_fim_de_semana
        ) VALUES (
            CURRENT_DATE,
            EXTRACT(YEAR FROM CURRENT_DATE),
            CASE WHEN EXTRACT(MONTH FROM CURRENT_DATE) <= 6 THEN 1 ELSE 2 END,
            EXTRACT(QUARTER FROM CURRENT_DATE),
            EXTRACT(MONTH FROM CURRENT_DATE),
            TO_CHAR(CURRENT_DATE, 'TMMonth'),
            EXTRACT(WEEK FROM CURRENT_DATE),
            EXTRACT(DAY FROM CURRENT_DATE),
            EXTRACT(ISODOW FROM CURRENT_DATE),
            TO_CHAR(CURRENT_DATE, 'TMDay'),
            CASE WHEN EXTRACT(ISODOW FROM CURRENT_DATE) IN (6, 7) THEN TRUE ELSE FALSE END
        ) RETURNING id_tempo INTO v_id_tempo;
    END IF;

    -- 2. Limpa registros de clima existentes para esta data para evitar duplicados
    DELETE FROM fato_clima WHERE id_tempo = v_id_tempo;

    -- 3. Obtém o mês atual para cálculo de sazonalidade
    v_month := EXTRACT(MONTH FROM CURRENT_DATE);
    -- Onda senoidal de sazonalidade: pico em junho (verão no norte, inverno no sul)
    v_sin_seasonal := sin((v_month - 3) * pi() / 6);

    -- 4. Para cada localidade com coordenadas válidas
    FOR loc_record IN 
        SELECT id_localidade, municipio, estado, regiao, pais, continente, latitude_ref, longitude_ref
        FROM dim_localidade 
        WHERE latitude_ref IS NOT NULL
    LOOP
        IF loc_record.pais = 'Brasil' THEN
            -- Clima realista por região no Brasil (Junho/Inverno)
            IF loc_record.regiao = 'Norte' THEN
                -- Quente e úmido / pouca variação sazonal
                v_temp_max := 31.0 + (random() * 4.0); -- 31 a 35°C
                v_temp_min := 22.0 + (random() * 3.0); -- 22 a 25°C
            ELSIF loc_record.regiao = 'Nordeste' THEN
                -- Quente / ligeiramente mais fresco no litoral
                v_temp_max := 28.0 + (random() * 4.0); -- 28 a 32°C
                v_temp_min := 20.0 + (random() * 3.0); -- 20 a 23°C
            ELSIF loc_record.regiao = 'Centro-Oeste' THEN
                -- Cuiabá continua bem quente, Brasília/Goiânia/Campo Grande mais frescos à noite
                IF loc_record.municipio = 'Cuiabá' THEN
                    v_temp_max := 31.0 + (random() * 4.0); -- 31 a 35°C
                    v_temp_min := 18.0 + (random() * 4.0); -- 18 a 22°C
                ELSE
                    v_temp_max := 26.0 + (random() * 4.0); -- 26 a 30°C
                    v_temp_min := 14.0 + (random() * 4.0); -- 14 a 18°C
                END IF;
            ELSIF loc_record.regiao = 'Sudeste' THEN
                -- Rio e Vitória (litoral) são amenos; SP e BH são mais frios (altitude)
                IF loc_record.municipio IN ('Vitória', 'Rio de Janeiro') THEN
                    v_temp_max := 24.0 + (random() * 4.0); -- 24 a 28°C (Vitória/ES máxima ideal ~27°C)
                    v_temp_min := 17.0 + (random() * 3.0); -- 17 a 20°C
                ELSE -- Belo Horizonte, São Paulo
                    v_temp_max := 20.0 + (random() * 4.0); -- 20 a 24°C
                    v_temp_min := 11.0 + (random() * 4.0); -- 11 a 15°C
                END IF;
            ELSIF loc_record.regiao = 'Sul' THEN
                -- Região mais fria do país no inverno
                v_temp_max := 15.0 + (random() * 5.0); -- 15 a 20°C
                v_temp_min := 6.0 + (random() * 6.0);  -- 6 a 12°C
            ELSE
                -- Padrão de segurança para o Brasil
                v_temp_max := 25.0 + (random() * 5.0);
                v_temp_min := 15.0 + (random() * 5.0);
            END IF;
            
            v_temp_med := (v_temp_max + v_temp_min) / 2.0;
        ELSE
            -- Fórmula matemática elegante e ciente de latitude para o resto do mundo
            -- Base: Temperatura média anual diminui à medida que nos afastamos do equador
            v_temp_med := 28.0 - 0.35 * abs(loc_record.latitude_ref);
            
            -- Amplitude: A variação de temperatura sazonal aumenta em latitudes maiores
            v_amp := 0.22 * abs(loc_record.latitude_ref);
            
            -- Aplicação sazonal:
            -- Se for no norte (latitude > 0), o pico da onda (junho) aumenta a temperatura
            -- Se for no sul (latitude < 0), o pico da onda (junho) reduz a temperatura
            IF loc_record.latitude_ref >= 0 THEN
                v_temp_med := v_temp_med + (v_amp * v_sin_seasonal);
            ELSE
                v_temp_med := v_temp_med - (v_amp * v_sin_seasonal);
            END IF;
            
            -- Adiciona variação diária randômica (-2°C a +2°C)
            v_temp_med := v_temp_med + (random() * 4.0 - 2.0);
            
            -- Define as máximas e mínimas em torno da média
            v_temp_max := v_temp_med + 3.0 + (random() * 4.0);
            v_temp_min := v_temp_med - 3.0 - (random() * 4.0);
        END IF;

        -- Arredondamento para 2 casas decimais
        v_temp_med := round(v_temp_med, 2);
        v_temp_max := round(v_temp_max, 2);
        v_temp_min := round(v_temp_min, 2);

        INSERT INTO fato_clima (
            id_tempo, id_localidade,
            temperatura_media, temperatura_max, temperatura_min,
            umidade_media, precipitacao_mm, velocidade_vento,
            direcao_vento, pressao_hpa, radiacao_solar
        ) VALUES (
            v_id_tempo, loc_record.id_localidade,
            v_temp_med, v_temp_max, v_temp_min,
            40 + (random() * 40), -- Umidade 40 a 80
            random() * 10, -- Precipitação
            random() * 30, -- Vento
            random() * 360, -- Direção Vento
            1000 + (random() * 20), -- Pressão
            random() * 1000 -- Radiação
        );
    END LOOP;
END $$;
