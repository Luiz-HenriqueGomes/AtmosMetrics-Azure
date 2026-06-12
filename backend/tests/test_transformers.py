# ============================================================
# AtmosMetrics — tests/test_transformers.py
# Testes unitários das funções puras de transformação ETL
# ============================================================

import sys, os
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

from datetime import date

# Importa diretamente sem precisar de banco de dados
from etl.transformers import construir_dim_tempo, ESTADO_PARA_UF


class TestConstruirDimTempo:
    """Testes para a função construir_dim_tempo do módulo transformers."""

    def test_construir_dim_tempo_campos_basicos(self):
        """Verifica se os campos básicos são preenchidos corretamente."""
        resultado = construir_dim_tempo(date(2025, 6, 10))

        assert resultado["data_completa"] == date(2025, 6, 10)
        assert resultado["ano"] == 2025
        assert resultado["mes"] == 6
        assert resultado["dia"] == 10

    def test_construir_dim_tempo_semestre(self):
        """Verifica o cálculo correto do semestre."""
        # Primeiro semestre (janeiro a junho)
        resultado_jan = construir_dim_tempo(date(2025, 1, 15))
        assert resultado_jan["semestre"] == 1

        resultado_jun = construir_dim_tempo(date(2025, 6, 30))
        assert resultado_jun["semestre"] == 1

        # Segundo semestre (julho a dezembro)
        resultado_jul = construir_dim_tempo(date(2025, 7, 1))
        assert resultado_jul["semestre"] == 2

        resultado_dez = construir_dim_tempo(date(2025, 12, 25))
        assert resultado_dez["semestre"] == 2

    def test_construir_dim_tempo_trimestre(self):
        """Verifica o cálculo correto do trimestre."""
        # Q1: jan-mar
        assert construir_dim_tempo(date(2025, 1, 1))["trimestre"] == 1
        assert construir_dim_tempo(date(2025, 3, 31))["trimestre"] == 1

        # Q2: abr-jun
        assert construir_dim_tempo(date(2025, 4, 1))["trimestre"] == 2
        assert construir_dim_tempo(date(2025, 6, 30))["trimestre"] == 2

        # Q3: jul-set
        assert construir_dim_tempo(date(2025, 7, 1))["trimestre"] == 3
        assert construir_dim_tempo(date(2025, 9, 30))["trimestre"] == 3

        # Q4: out-dez
        assert construir_dim_tempo(date(2025, 10, 1))["trimestre"] == 4
        assert construir_dim_tempo(date(2025, 12, 31))["trimestre"] == 4

    def test_construir_dim_tempo_nomes_portugues(self):
        """Verifica se os nomes dos meses e dias estão em português."""
        # Janeiro = mês 1
        resultado_jan = construir_dim_tempo(date(2025, 1, 6))  # Segunda-feira
        assert resultado_jan["nome_mes"] == "Janeiro"

        # Dezembro = mês 12
        resultado_dez = construir_dim_tempo(date(2025, 12, 25))
        assert resultado_dez["nome_mes"] == "Dezembro"

        # Verifica que nome_dia é string válida em português
        resultado = construir_dim_tempo(date(2025, 6, 10))  # Terça-feira
        assert resultado["nome_dia"] == "Terça-feira"

    def test_construir_dim_tempo_fim_de_semana(self):
        """Verifica a detecção correta de dias úteis e fins de semana."""
        # 2025-06-10 é Terça-feira (dia útil)
        resultado_terca = construir_dim_tempo(date(2025, 6, 10))
        assert resultado_terca["e_fim_de_semana"] is False

        # 2025-06-14 é Sábado (fim de semana)
        resultado_sabado = construir_dim_tempo(date(2025, 6, 14))
        assert resultado_sabado["e_fim_de_semana"] is True

        # 2025-06-15 é Domingo (fim de semana)
        resultado_domingo = construir_dim_tempo(date(2025, 6, 15))
        assert resultado_domingo["e_fim_de_semana"] is True

        # 2025-06-13 é Sexta-feira (dia útil)
        resultado_sexta = construir_dim_tempo(date(2025, 6, 13))
        assert resultado_sexta["e_fim_de_semana"] is False


class TestEstadoParaUF:
    """Testes para o dicionário ESTADO_PARA_UF."""

    def test_estado_para_uf_mapeamento_27_entradas(self):
        """O Brasil tem 27 unidades federativas (26 estados + DF)."""
        assert len(ESTADO_PARA_UF) == 27

    def test_estado_para_uf_mapeamentos_corretos(self):
        """Verifica alguns mapeamentos específicos conhecidos."""
        assert ESTADO_PARA_UF["São Paulo"] == "SP"
        assert ESTADO_PARA_UF["Minas Gerais"] == "MG"
        assert ESTADO_PARA_UF["Rio de Janeiro"] == "RJ"
        assert ESTADO_PARA_UF["Bahia"] == "BA"
        assert ESTADO_PARA_UF["Amazonas"] == "AM"
        assert ESTADO_PARA_UF["Distrito Federal"] == "DF"
        assert ESTADO_PARA_UF["Mato Grosso"] == "MT"
        assert ESTADO_PARA_UF["Paraná"] == "PR"
