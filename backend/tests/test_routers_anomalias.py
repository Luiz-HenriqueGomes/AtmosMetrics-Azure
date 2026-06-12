# ============================================================
# AtmosMetrics — tests/test_routers_anomalias.py
# Testes de integração dos endpoints /api/v1/anomalias
# ============================================================


class TestListarAnomalias:
    """Testes para o endpoint GET /api/v1/anomalias/."""

    def test_listar_anomalias_retorna_200(self, client, seed_data):
        """GET /api/v1/anomalias/ deve retornar status 200."""
        response = client.get("/api/v1/anomalias/")
        assert response.status_code == 200

    def test_listar_anomalias_retorna_lista(self, client, seed_data):
        """Resposta deve ser uma lista."""
        response = client.get("/api/v1/anomalias/")
        data = response.json()
        assert isinstance(data, list)

    def test_listar_anomalias_paginacao_limit(self, client, seed_data):
        """Parâmetro limit deve controlar o número de resultados."""
        response = client.get("/api/v1/anomalias/", params={"limit": 1})
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1


class TestResumoAnomalias:
    """Testes para o endpoint GET /api/v1/anomalias/resumo."""

    def test_resumo_anomalias_retorna_200(self, client, seed_data):
        """GET /api/v1/anomalias/resumo deve retornar status 200."""
        response = client.get("/api/v1/anomalias/resumo")
        assert response.status_code == 200

    def test_resumo_anomalias_campos_esperados(self, client, seed_data):
        """Resumo deve conter os campos agregados do schema ResumoGeralOut."""
        response = client.get("/api/v1/anomalias/resumo")
        data = response.json()
        assert "total_focos" in data
        assert "media_frp" in data
        assert "media_risco" in data
        assert "por_uf" in data
        assert "por_bioma" in data
        assert "por_pais" in data
        assert "por_continente" in data
        assert data["total_focos"] >= 1
