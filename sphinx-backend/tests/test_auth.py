def test_login_success(client, doctor_user):
    res = client.post('/api/v1/auth/login', json={
        'email': 'testdoctor@sphinx.com',
        'password': 'DoctorPass123!'
    })
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['status'] == 'success'
    assert 'access_token' in json_data['data']
    assert 'refresh_token' in json_data['data']


def test_login_invalid_credentials(client):
    res = client.post('/api/v1/auth/login', json={
        'email': 'wrong@sphinx.com',
        'password': 'WrongPassword!'
    })
    assert res.status_code == 401
    assert res.get_json()['status'] == 'error'


def test_protected_route_unauthorized(client):
    res = client.get('/api/v1/patients')
    assert res.status_code == 401
