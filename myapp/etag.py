from flask import Blueprint, request, make_response, jsonify
from datetime import datetime
import hashlib

etag_bp = Blueprint('etag', __name__)
persons_database = {}


@etag_bp.route('/persons', methods=['GET'])
def persons_get():
    result = []
    for person_id in persons_database:
        result.append({
            'person_id': person_id,
            'person_name': persons_database[person_id]['person_name'],
            'change_date': persons_database[person_id]['change_date'],
            'etag': persons_database[person_id]['etag']
        })
    return jsonify(result), 200


@etag_bp.route('/persons/<person_id>', methods=['GET'])
def person_get(person_id):
    if person_id not in persons_database:
        return jsonify(message=f'Person with ID {person_id} not found'), 404
    person = persons_database[person_id]
    if_none_match = request.if_none_match
    if if_none_match.contains(person['etag']):
        return jsonify(message='OK'), 304
    else:
        response = make_response(dict(person_id=person_id,
                                      person_name=person['person_name'],
                                      change_date=person['change_date'],
                                      etag=person['etag']))
        response.headers['ETag'] = person['etag']
        return response, 200


@etag_bp.route('/persons', methods=['POST'])
def person_create():
    if not request.is_json:
        return jsonify(message='Missing JSON data in request'), 400
    data = request.get_json()
    person_id = data.get('person_id')
    person_name = data.get('person_name')
    change_date = datetime.utcnow().isoformat()
    etag = hashlib.md5(change_date.encode()).hexdigest()
    if not person_id:
        return jsonify(message=f'Person ID is mandatory'), 400
    if not person_name:
        return jsonify(message=f'Person name is mandatory'), 400
    if person_id in persons_database:
        return jsonify(message=f'Person with ID {person_id} already exists'), 400
    persons_database[person_id] = {
        'person_name': person_name,
        'change_date': change_date,
        'etag': etag
    }
    response = make_response(dict(person_id=person_id,
                                  person_name=person_name,
                                  change_date=change_date,
                                  etag=etag))
    response.headers['ETag'] = etag
    return response, 201


@etag_bp.route('/persons/<person_id>', methods=['PUT'])
def person_update(person_id):
    pass
