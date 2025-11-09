import os
import sys

# Agrega la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_login_route():
    response = client.post("/login", json={"email": "prueba@test.com", "password": "1234"})
    assert response.status_code in [200, 401]
