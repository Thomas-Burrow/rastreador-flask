def test_api_veh_placa_bom(client):  # podemos loca
    response = client.get("/api/veiculo/por_placa/AAA-1234")
    assert response.status_code == 200  # conforme especificação http
    assert b"AAA-1234" in response.data
    assert (
        b"Teste" in response.data
    )  # Teste se localiza a ultima entrada para placa quande existirem multiplas entradas


def test_api_veh_placa_bom_2(client):  # podemos loca
    response = client.get(
        "/api/veiculo/por_placa/XYZ12C4"
    )  # tambem funciona com placas no novo formato
    assert response.status_code == 200  # conforme especificação http
    assert b"XYZ12C4" in response.data


def test_api_veh_placa_caseinsensitivo(
    client,
):  # letras podem ser maiusculas ou minusculas
    response = client.get("/api/veiculo/por_placa/aaa-1234")
    assert response.status_code == 200
    assert b"AAA-1234" in response.data
    assert b"Teste" in response.data


def test_api_veh_placa_ruim(client):
    response = client.get("/api/veiculo/por_placa/ZZZ-9999")
    assert response.status_code == 404  # Tambem conhecido como: não encontrado


def test_api_veh_id_3(client):
    response = client.get("/api/veiculo/por_id/3")
    assert response.status_code == 200
    assert b"XYZ12C4" in response.data
    assert b"Oficina" in response.data


def test_api_veh_id_2(client):
    response = client.get("/api/veiculo/por_id/2")
    assert response.status_code == 200
    assert b"AAA-1234" in response.data
    assert b"Teste" in response.data


def test_api_veh_id_1(client):
    response = client.get("/api/veiculo/por_id/1")
    assert response.status_code == 200
    assert b"AAA-1234" in response.data
    assert b"Retirado" in response.data
