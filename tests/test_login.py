def test_login_valid_credentials(client, auth):
    # Assume 'testuser' and 'password' are pre-registered or registered in a setup fixture
    response = auth.login("test", "test")
    assert response.status_code == 302


def test_login_valid_credentials_2(client, auth):
    # Assume 'testuser' and 'password' are pre-registered or registered in a setup fixture
    response = auth.login("other", "test")
    assert response.status_code == 302


def test_login_invalid_credentials(client, auth):
    # Assume 'testuser' and 'password' are pre-registered or registered in a setup fixture
    response = auth.login("other", "other")
    assert response.status_code == 200  # não redirecionou neste caso
