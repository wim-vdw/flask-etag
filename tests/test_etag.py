def test_person_create(client):
    person_id = '1'
    person_name = 'Wim'
    response = client.post('/persons', json={person_id: person_id, person_name: person_name})
    assert response.status_code == 201
    data = response.get_json()
    assert 'person_id' in data
    assert 'person_name' in data
    assert 'change_date' in data
    assert 'etag' in data
    assert 'ETag' in response.headers
