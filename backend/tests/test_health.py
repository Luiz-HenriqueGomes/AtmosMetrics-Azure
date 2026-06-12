# ============================================================
# AtmosMetrics — tests/test_health.py
# Testes do endpoint de health check (GET /)
# ============================================================

from unittest.mock import patch


class TestHealthCheck:
    """Testes para o endpoint de verificação de saúde da API."""

    def test_health_check_retorna_200(self, client):
        """GET / deve retornar status code 200."""
        with patch("app.main.check_connection", return_value=True):
            response = client.get("/")
        assert response.status_code == 200

    def test_health_check_possui_campos_obrigatorios(self, client):
        """Resposta deve conter os campos 'status' e 'api'."""
        with patch("app.main.check_connection", return_value=True):
            response = client.get("/")
        data = response.json()
        assert "status" in data
        assert "api" in data
        assert data["status"] == "online"
        assert data["api"] == "AtmosMetrics"

    def test_health_check_banco_desconectado(self, client):
        """Quando o banco está desconectado, campo 'banco' deve indicar isso."""
        with patch("app.main.check_connection", return_value=False):
            response = client.get("/")
        data = response.json()
        assert response.status_code == 200
        assert data["banco"] == "desconectado"
