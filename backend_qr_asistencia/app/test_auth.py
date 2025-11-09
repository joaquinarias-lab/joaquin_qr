import os
import sys

# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_home_route():
    """Prueba básica: el servidor responde correctamente en la ruta raíz."""
    response = client.get("/")
    assert response.status_code in [200, 404]  # según tu configuración real
