from flask import Blueprint

etag_bp = Blueprint('etag', __name__)


@etag_bp.route('/')
def index():
    return 'Hello'
