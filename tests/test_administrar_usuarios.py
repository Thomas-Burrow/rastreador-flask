def test_users_as_guest(client):
    response = client.get('/users')
    assert response.status_code == 302

def test_users_without_correct_perms(client, auth):
    auth.login('other', 'test')
    response = client.get('/users')
    assert response.status_code == 403

def test_users_as_logged_in_user(client, auth):
    auth.login('test', 'test')
    response = client.get('/users')
    assert response.status_code == 200

def test_user_edit_as_guest(client):
    response = client.get('/alterar_cargo/1')
    assert response.status_code == 302

def test_user_edit_without_correct_perms(client, auth):
    auth.login('other', 'test')
    response = client.get('/alterar_cargo/1')
    assert response.status_code == 403

def test_user_edit_as_logged_in_user(client, auth):
    auth.login('test', 'test')
    response = client.get('/alterar_cargo/1')
    assert response.status_code == 200