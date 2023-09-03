import pytest

testdata = [('1', 'Wim Van den Wyngaert'), ('2', 'Bill Gates'), ('3', 'Cristiano Ronaldo')]
testdata_does_not_exist = ['100', '101', '102']


def test_person_create_missing_json_data(client):
    response = client.post('/persons')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Missing JSON data in request'


def test_person_create_missing_fields(client):
    response = client.post('/persons', json={"field-not-needed-in-check": 1})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Person ID is mandatory'
    response = client.post('/persons', json={"person_id": "1"})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Person name is mandatory'


@pytest.mark.parametrize('person_id, person_name', testdata)
def test_person_create(client, person_id, person_name):
    response = client.post('/persons', json={"person_id": person_id, "person_name": person_name})
    assert response.status_code == 201
    data = response.get_json()
    assert 'person_id' in data
    assert 'person_name' in data
    assert 'change_date' in data
    assert 'ETag' in response.headers
    assert data['person_id'] == person_id
    assert data['person_name'] == person_name
    response = client.post('/persons', json={"person_id": person_id, "person_name": person_name})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == f'Person with ID {person_id} already exists'


def test_person_get_list(client):
    response = client.get('/persons')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


@pytest.mark.parametrize('person_id, person_name', testdata)
def test_person_get(client, person_id, person_name):
    response = client.get(f'/persons/{person_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'person_id' in data
    assert 'person_name' in data
    assert 'change_date' in data
    assert 'ETag' in response.headers
    etag = response.headers['ETag']
    response = client.get(f'/persons/{person_id}', headers={'If-None-Match': etag})
    assert response.status_code == 304


@pytest.mark.parametrize('person_id', testdata_does_not_exist)
def test_person_get_not_found(client, person_id):
    response = client.get(f'/persons/{person_id}')
    assert response.status_code == 404
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == f'Person with ID {person_id} not found'


@pytest.mark.parametrize('person_id, person_name', testdata)
def test_person_update_missing_json_data(client, person_id, person_name):
    response = client.put(f'/persons/{person_id}')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Missing JSON data in request'


@pytest.mark.parametrize('person_id, person_name', testdata)
def test_person_update_missing_fields(client, person_id, person_name):
    response = client.put(f'/persons/{person_id}', json={'field-not-needed-in-check': 1})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Person name is mandatory'


@pytest.mark.parametrize('person_id, person_name', testdata)
def test_person_update(client, person_id, person_name):
    response = client.get(f'/persons/{person_id}')
    assert response.status_code == 200
    data = response.get_json()
    person_id = data['person_id']
    person_name = data['person_name'] + 'blablabla1'
    etag = response.headers['ETag']
    response = client.put(f'/persons/{person_id}', json={"person_name": person_name})
    assert response.status_code == 412
    data = response.get_json()
    assert data['message'] == 'Data already changed, get recent resource data and ETag first'
    response = client.put(f'/persons/{person_id}', json={"person_name": person_name}, headers={'If-Match': etag})
    assert response.status_code == 200


@pytest.mark.parametrize('person_id', testdata_does_not_exist)
def test_person_update_not_found(client, person_id):
    response = client.put(f'/persons/{person_id}')
    assert response.status_code == 404
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == f'Person with ID {person_id} not found'
