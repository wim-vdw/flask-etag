import pytest

testdata = [('1', 'Wim Van den Wyngaert'), ('2', 'Bill Gates'), ('3', 'Cristiano Ronaldo')]


def test_person_create_missing_json_data(client):
    response = client.post('/persons')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Missing JSON data in request'


def test_person_create_missing_fields(client):
    response = client.post('/persons', json={})
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
    assert 'etag' in data
    assert 'ETag' in response.headers
    assert data['person_id'] == person_id
    assert data['person_name'] == person_name
    response = client.post('/persons', json={"person_id": person_id, "person_name": person_name})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == f'Person with ID {person_id} already exists'
