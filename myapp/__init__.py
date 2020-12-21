from flask import Flask


def create_app():
    app = Flask(__name__)
    from myapp.etag import etag_bp
    app.register_blueprint(etag_bp)

    return app
