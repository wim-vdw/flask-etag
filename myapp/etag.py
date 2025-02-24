from flask import Blueprint, request, make_response, jsonify
from datetime import datetime, timezone
import hashlib

etag_bp = Blueprint('etag', __name__)
persons_database = {}


@etag_bp.route('/')
def index():
    result = {'foo': 'bar'}
    return jsonify(result), 200


@etag_bp.route('/persons', methods=['GET'])
def persons_get():
    result = []
    for person_id in persons_database:
        result.append({
            'person_id': person_id,
            'person_name': persons_database[person_id]['person_name'],
            'change_date': persons_database[person_id]['change_date']
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
    response = make_response(dict(person_id=person_id,
                                  person_name=person['person_name'],
                                  change_date=person['change_date']))
    response.set_etag(person['etag'])
    return response, 200


@etag_bp.route('/persons', methods=['POST'])
def person_create():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify(message='Missing JSON data in request'), 400
    person_id = data.get('person_id')
    person_name = data.get('person_name')
    change_date = datetime.now(timezone.utc).isoformat()
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
                                  change_date=change_date))
    response.set_etag(etag)
    return response, 201


@etag_bp.route('/persons/<person_id>', methods=['PUT'])
def person_update(person_id):
    if person_id not in persons_database:
        return jsonify(message=f'Person with ID {person_id} not found'), 404
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify(message='Missing JSON data in request'), 400
    person_name = data.get('person_name')
    if not person_name:
        return jsonify(message=f'Person name is mandatory'), 400
    person = persons_database[person_id]
    etag = person['etag']
    if_match = request.if_match
    if not if_match.contains(etag):
        return jsonify(message='Data already changed, get recent resource data and ETag first'), 412
    change_date = datetime.now(timezone.utc).isoformat()
    new_etag = hashlib.md5(change_date.encode()).hexdigest()
    persons_database[person_id] = {
        'person_name': person_name,
        'change_date': change_date,
        'etag': new_etag
    }
    response = make_response(dict(person_id=person_id,
                                  person_name=person_name,
                                  change_date=change_date))
    response.set_etag(new_etag)
    return response, 200
