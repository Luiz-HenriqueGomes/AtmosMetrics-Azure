# ============================================================
# AtmosMetrics — tests/test_routers_qualidade_ar.py
# Testes de integração dos endpoints /api/v1/qualidade-ar
# ============================================================


class TestListarQualidadeAr:
    """Testes para o endpoint GET /api/v1/qualidade-ar/."""

    def test_listar_qualidade_ar_retorna_200(self, client, seed_data):
        """GET /api/v1/qualidade-ar/ deve retornar status 200."""
        response = client.get("/api/v1/qualidade-ar/")
        assert response.status_code == 200

    def test_listar_qualidade_ar_retorna_lista(self, client, seed_data):
        """Resposta deve ser uma lista com pelo menos 1 registro."""
        response = client.get("/api/v1/qualidade-ar/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestResumoQualidadeAr:
    """Testes para o endpoint GET /api/v1/qualidade-ar/resumo."""

    def test_resumo_qualidade_ar_retorna_200(self, client, seed_data):
        """GET /api/v1/qualidade-ar/resumo deve retornar status 200."""
        response = client.get("/api/v1/qualidade-ar/resumo")
        assert response.status_code == 200

    def test_resumo_qualidade_ar_campos_esperados(self, client, seed_data):
        """Resumo deve conter os campos agregados esperados."""
        response = client.get("/api/v1/qualidade-ar/resumo")
        data = response.json()
        assert "total_medicoes" in data
        assert "aqi_medio" in data
        assert "pm25_medio" in data
        assert "pm10_medio" in data
        assert "co_medio" in data
        assert data["total_medicoes"] >= 1
