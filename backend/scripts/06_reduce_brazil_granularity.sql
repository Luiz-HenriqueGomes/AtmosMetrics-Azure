-- Deleta os dados de granularidade fina do Brasil (municípios do interior)
-- Mantendo apenas as capitais de cada estado para média granularidade, assim como no mundo todo.

DO $$
DECLARE
    v_capitais TEXT[] := ARRAY[
        'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 
        'Curitiba', 'Porto Alegre', 'Salvador', 'Fortaleza', 'Recife', 
        'Manaus', 'Belém', 'Goiânia', 'Cuiabá', 'Campo Grande', 
        'Florianópolis', 'Vitória', 'Natal', 'João Pessoa', 'Maceió', 
        'Aracaju', 'São Luís', 'Teresina', 'Palmas', 'Macapá', 
        'Boa Vista', 'Rio Branco', 'Porto Velho'
    ];
BEGIN
    -- Deleta as anomalias e qualidade do ar para cidades do Brasil que não estão no array
    DELETE FROM fato_qualidade_ar 
    WHERE id_localidade IN (
        SELECT id_localidade FROM dim_localidade 
        WHERE pais = 'Brasil' AND municipio != ALL(v_capitais)
    );

    DELETE FROM fato_clima 
    WHERE id_localidade IN (
        SELECT id_localidade FROM dim_localidade 
        WHERE pais = 'Brasil' AND municipio != ALL(v_capitais)
    );
    
    DELETE FROM fato_anomalia_termica
    WHERE id_localidade IN (
        SELECT id_localidade FROM dim_localidade 
        WHERE pais = 'Brasil' AND municipio != ALL(v_capitais)
    );

    -- Deleta as próprias localidades (dimensão)
    DELETE FROM dim_localidade 
    WHERE pais = 'Brasil' AND municipio != ALL(v_capitais);
END $$;
