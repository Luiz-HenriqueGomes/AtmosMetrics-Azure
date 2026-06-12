-- ============================================================
-- AtmosMetrics — Desduplicação de Localidades Globais
-- ============================================================

-- Remove registros duplicados criados por execuções concorrentes
-- ou de esquemas com codificação corrompida. Mantém apenas uma
-- cópia limpa e estruturada com estados/regiões de cada cidade global.

DO $$
BEGIN
    -- 1. Remover referências a localidades com codificação corrompida (ex: 'Austr??lia')
    DELETE FROM fato_clima WHERE id_localidade IN (
        SELECT id_localidade FROM dim_localidade 
        WHERE pais LIKE '%?%' OR estado LIKE '%?%' OR municipio LIKE '%?%' OR regiao LIKE '%?%'
    );
    
    DELETE FROM fato_qualidade_ar WHERE id_localidade IN (
        SELECT id_localidade FROM dim_localidade 
        WHERE pais LIKE '%?%' OR estado LIKE '%?%' OR municipio LIKE '%?%' OR regiao LIKE '%?%'
    );
    
    DELETE FROM dim_localidade 
    WHERE pais LIKE '%?%' OR estado LIKE '%?%' OR municipio LIKE '%?%' OR regiao LIKE '%?%';

    -- 2. Identificar e apagar registros duplicados com coordenadas idênticas.
    -- Dá preferência para manter o registro que possui 'estado' preenchido (média granularidade).
    -- Depois disso, dá preferência ao id_localidade menor.
    
    -- Excluir de fato_clima
    WITH duplicates AS (
        SELECT id_localidade,
               ROW_NUMBER() OVER (
                   PARTITION BY round(latitude_ref, 4), round(longitude_ref, 4)
                   ORDER BY CASE WHEN estado IS NOT NULL THEN 1 ELSE 2 END, id_localidade ASC
               ) as rn
        FROM dim_localidade
        WHERE latitude_ref IS NOT NULL
    )
    DELETE FROM fato_clima WHERE id_localidade IN (
        SELECT id_localidade FROM duplicates WHERE rn > 1
    );

    -- Excluir de fato_qualidade_ar
    WITH duplicates AS (
        SELECT id_localidade,
               ROW_NUMBER() OVER (
                   PARTITION BY round(latitude_ref, 4), round(longitude_ref, 4)
                   ORDER BY CASE WHEN estado IS NOT NULL THEN 1 ELSE 2 END, id_localidade ASC
               ) as rn
        FROM dim_localidade
        WHERE latitude_ref IS NOT NULL
    )
    DELETE FROM fato_qualidade_ar WHERE id_localidade IN (
        SELECT id_localidade FROM duplicates WHERE rn > 1
    );

    -- Excluir de dim_localidade
    WITH duplicates AS (
        SELECT id_localidade,
               ROW_NUMBER() OVER (
                   PARTITION BY round(latitude_ref, 4), round(longitude_ref, 4)
                   ORDER BY CASE WHEN estado IS NOT NULL THEN 1 ELSE 2 END, id_localidade ASC
               ) as rn
        FROM dim_localidade
        WHERE latitude_ref IS NOT NULL
    )
    DELETE FROM dim_localidade WHERE id_localidade IN (
        SELECT id_localidade FROM duplicates WHERE rn > 1
    );

END $$;
