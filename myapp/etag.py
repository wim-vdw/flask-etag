from flask import Blueprint, request, make_response
from datetime import datetime
import hashlib

etag_bp = Blueprint('etag', __name__)
persons_database = {}


@etag_bp.route('/persons', methods=['GET'])
def persons_get():
    pass


@etag_bp.route('/persons/<person_id>', methods=['GET'])
def person_get(person_id):
    pass


@etag_bp.route('/persons', methods=['POST'])
def person_create():
    data = request.get_json()
    person_id = data.get('person_id')
    person_name = data.get('person_name')
    change_date = datetime.utcnow().isoformat()
    etag = hashlib.md5(change_date.encode()).hexdigest()
    response = make_response(dict(person_id=person_id,
                                  person_name=person_name,
                                  change_date=change_date,
                                  etag=etag))
    response.headers['ETag'] = etag
    return response, 201


@etag_bp.route('/persons/<person_id>', methods=['PUT'])
def person_update(person_id):
    pass
