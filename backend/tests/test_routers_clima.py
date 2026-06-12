# ============================================================
# AtmosMetrics — tests/test_routers_clima.py
# Testes de integração dos endpoints /api/v1/clima
# ============================================================


class TestListarClima:
    """Testes para o endpoint GET /api/v1/clima/."""

    def test_listar_clima_retorna_200(self, client, seed_data):
        """GET /api/v1/clima/ deve retornar status 200."""
        response = client.get("/api/v1/clima/")
        assert response.status_code == 200

    def test_listar_clima_retorna_lista(self, client, seed_data):
        """Resposta deve ser uma lista (array JSON)."""
        response = client.get("/api/v1/clima/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_listar_clima_contem_campos_esperados(self, client, seed_data):
        """Cada registro deve conter os campos essenciais do schema ClimaOut."""
        response = client.get("/api/v1/clima/")
        data = response.json()
        registro = data[0]
        assert "id_clima" in registro
        assert "temperatura_media" in registro
        assert "municipio" in registro
        assert "pais" in registro


class TestResumoClima:
    """Testes para o endpoint GET /api/v1/clima/resumo."""

    def test_resumo_clima_retorna_200(self, client, seed_data):
        """GET /api/v1/clima/resumo deve retornar status 200."""
        response = client.get("/api/v1/clima/resumo")
        assert response.status_code == 200

    def test_resumo_clima_campos_esperados(self, client, seed_data):
        """Resumo deve conter os campos agregados esperados."""
        response = client.get("/api/v1/clima/resumo")
        data = response.json()
        assert "total_registros" in data
        assert "temp_media_global" in data
        assert "temp_max_global" in data
        assert "temp_min_global" in data
        assert "umidade_media" in data
        assert data["total_registros"] >= 1


class TestExtremas:
    """Testes para o endpoint GET /api/v1/clima/extremas."""

    def test_extremas_retorna_200(self, client, seed_data):
        """GET /api/v1/clima/extremas deve retornar status 200."""
        response = client.get("/api/v1/clima/extremas")
        assert response.status_code == 200

    def test_extremas_retorna_lista(self, client, seed_data):
        """Resposta deve ser uma lista."""
        response = client.get("/api/v1/clima/extremas")
        data = response.json()
        assert isinstance(data, list)
