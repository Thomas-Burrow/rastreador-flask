def test_dash_as_guest(client):
    response = client.get("/dash")
    assert response.status_code == 200  # dashboard é visivel para todos no momento


def test_dash_without_correct_perms(client, auth):
    auth.login("other", "test")
    response = client.get("/dash")
    assert response.status_code == 200


def test_dash_as_logged_in_user(client, auth):
    auth.login("test", "test")
    response = client.get("/dash")
    assert response.status_code == 200


def test_scan_as_guest(client):
    response = client.get("/scan/1")
    assert response.status_code == 302


def test_scan_without_correct_perms(client, auth):
    auth.login("other", "test")
    response = client.get("/scan/1")
    assert response.status_code == 403


def test_scan_as_logged_in_user(client, auth):
    auth.login("test", "test")
    response = client.get("/scan/1")
    assert response.status_code == 200
