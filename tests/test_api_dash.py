def test_api_dash_status(client):
    response = client.get("/api/veiculos")
    assert response.status_code == 200


def test_api_dash_values(client):
    response = client.get("/api/veiculos")
    assert b"AAA-1234" in response.data
    assert b"XYZ12C4" in response.data
