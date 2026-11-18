from tests.conftest import register_and_login

def test_home_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MISION ANDINA" in response.data

def test_register_login_dashboard(client):
    response = register_and_login(client)
    assert response.status_code == 200
    assert b"Panel de control" in response.data

def test_mission_crud_and_simulation(client):
    register_and_login(client)
    data = {"name":"Exploracion Marte","objective":"Analizar suelo marciano",
            "destination":"Marte","spacecraft":"Andina-1","launcher":"Lanzador pesado",
            "instruments":"Camara, espectrometro","budget":"180","mass":"950",
            "power":"800","communications":"Avanzada"}
    response = client.post("/misiones/nueva", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Exploracion Marte" in response.data
    response = client.post("/misiones/1/simular", follow_redirects=True)
    assert response.status_code == 200
    assert b"Exitosa" in response.data
    response = client.post("/misiones/1/eliminar", follow_redirects=True)
    assert response.status_code == 200
    assert b"Exploracion Marte" not in response.data

def test_missions_require_login(client):
    response = client.get("/misiones")
    assert response.status_code == 302
