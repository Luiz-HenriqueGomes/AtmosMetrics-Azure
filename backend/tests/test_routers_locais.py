# ============================================================
# AtmosMetrics — tests/test_routers_locais.py
# Testes de integração dos endpoints /api/v1/localidades
# ============================================================


class TestListarLocalidades:
    """Testes para o endpoint GET /api/v1/localidades/."""

    def test_listar_localidades_retorna_200(self, client, seed_data):
        """GET /api/v1/localidades/ deve retornar status 200."""
        response = client.get("/api/v1/localidades/")
        assert response.status_code == 200

    def test_listar_localidades_retorna_lista(self, client, seed_data):
        """Resposta deve ser uma lista com pelo menos 1 localidade."""
        response = client.get("/api/v1/localidades/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestListarPaises:
    """Testes para o endpoint GET /api/v1/localidades/paises."""

    def test_listar_paises_retorna_200(self, client, seed_data):
        """GET /api/v1/localidades/paises deve retornar status 200."""
        response = client.get("/api/v1/localidades/paises")
        assert response.status_code == 200

    def test_listar_paises_retorna_lista(self, client, seed_data):
        """Resposta deve conter pelo menos 1 país (Brasil, do seed)."""
        response = client.get("/api/v1/localidades/paises")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestListarContinentes:
    """Testes para o endpoint GET /api/v1/localidades/continentes."""

    def test_listar_continentes_retorna_200(self, client, seed_data):
        """GET /api/v1/localidades/continentes deve retornar status 200."""
        response = client.get("/api/v1/localidades/continentes")
        assert response.status_code == 200

    def test_listar_continentes_retorna_lista(self, client, seed_data):
        """Resposta deve conter pelo menos 1 continente."""
        response = client.get("/api/v1/localidades/continentes")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestListarEstados:
    """Testes para o endpoint GET /api/v1/localidades/estados."""

    def test_listar_estados_retorna_200(self, client, seed_data):
        """GET /api/v1/localidades/estados deve retornar status 200."""
        response = client.get("/api/v1/localidades/estados")
        assert response.status_code == 200

    def test_listar_estados_retorna_lista(self, client, seed_data):
        """Resposta deve conter pelo menos 1 estado (SP, do seed)."""
        response = client.get("/api/v1/localidades/estados")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
