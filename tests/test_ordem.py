def test_criar_as_guest(client):
    response = client.get('/ordem/criar')
    assert response.status_code == 302

def test_criar_without_correct_perms(client, auth):
    auth.login('other', 'test')
    response = client.get('/ordem/criar')
    assert response.status_code == 403

def test_criar_as_logged_in_user(client, auth):
    auth.login('test', 'test')
    response = client.get('/ordem/criar')
    assert response.status_code == 200

def test_qrcode_as_guest(client):
    response = client.get('/ordem/qrcode/1')
    assert response.status_code == 302

def test_qrcode_without_correct_perms(client, auth):
    auth.login('other', 'test')
    response = client.get('/ordem/qrcode/1')
    assert response.status_code == 403

def test_qrcode_as_logged_in_user(client, auth):
    auth.login('test', 'test')
    response = client.get('/ordem/qrcode/1')
    assert response.status_code == 200