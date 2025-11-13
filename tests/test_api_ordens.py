def test_ordens_por_placa(client):
    response = client.get("/api/ordens/por_placa/AAA-1234")
    assert response.status_code == 200
    assert b"2025" in response.data
    assert b"AAA-1234" in response.data


def test_ordens_por_placa_2(client):
    response = client.get("/api/ordens/por_placa/XYZ12C4")
    assert response.status_code == 200
    assert b"null" in response.data
    assert b"XYZ12C4" in response.data


def test_ordens_por_placa_caseinsentivo(client):
    response = client.get("/api/ordens/por_placa/xyz12C4")
    assert response.status_code == 200
    assert b"null" in response.data
    assert b"XYZ12C4" in response.data


def test_ordens_por_placa_ruim(client):
    response = client.get("/api/ordens/por_placa/ZZZ-9999")
    assert response.status_code == 404
