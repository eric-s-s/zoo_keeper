from functools import partial

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from zoo_keeper_server import USER, DB
from zoo_keeper_server.db_request_handler import DBRequestHandler, BadData, BadId
from zoo_keeper_server.data_base_session import DataBaseSession, data_base_session_scope


app = Flask(__name__)
app.config.from_object('zoo_keeper_server.flask_app_default_config')
try:
    app.config.from_envvar('APP_CONFIG')
    print('using config:')
    print(app.config)
except RuntimeError:
    print('using default config')

app_engine = create_engine(
    "mysql://{}@{}/{}".format(USER, app.config.get('DB_HOST_NAME'), DB),
    encoding='latin1'
)

DataBaseSession.configure(bind=app_engine)

ZOO_SERVICE_URL = app.config.get('ZOO_SERVICE_URL')


@app.route('/zoos/', methods=['GET'])
def all_zoos():
    with data_base_session_scope() as session:
        handler = DBRequestHandler(session, ZOO_SERVICE_URL)
        return handler.get_all_zoos()


@app.route('/monkeys/', methods=['GET'])
def all_monkeys():
    with data_base_session_scope() as session:
        handler = DBRequestHandler(session, ZOO_SERVICE_URL)
        return handler.get_all_monkeys()


@app.route('/zoo_keepers/', methods=['GET', 'POST'])
def all_zoo_keepers():
    with data_base_session_scope() as session:
        handler = DBRequestHandler(session, ZOO_SERVICE_URL)
        method = _get_method()

        request_json = _get_json()

        actions = {
            'GET': partial(handler.get_all_zoo_keepers),
            'POST': partial(handler.post_zoo_keeper, request_json),
        }
        reply = actions[method]()
    return reply


@app.route('/zoo_keepers/<zoo_keeper_id>', methods=['GET', 'PUT', 'DELETE'])
def single_zoo_keeper(zoo_keeper_id):
    with data_base_session_scope() as session:
        handler = DBRequestHandler(session, ZOO_SERVICE_URL)
        method = _get_method()

        request_json = _get_json()

        actions = {
            'GET': partial(handler.get_zoo_keeper, zoo_keeper_id),
            'PUT': partial(handler.put_zoo_keeper, zoo_keeper_id, request_json),
            'DELETE': partial(handler.delete_zoo_keeper, zoo_keeper_id)
        }
        reply = actions[method]()
    return reply


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    code = 400
    e_type = e.__class__.__name__
    text = str(e)
    title = "bad request"
    return jsonify(error=code, title=title, error_type=e_type, text=text), code


@app.errorhandler(OperationalError)
def handle_db_not_responding(e):
    code = 500
    e_type = e.__class__.__name__
    text = e.args[0]
    title = "db trouble"
    return jsonify(error=code, title=title, error_type=e_type, text=text), code


@app.errorhandler(404)
def handle_not_found(e):
    return jsonify(error=404, title="not found", text=str(e)), 404


@app.errorhandler(BadId)
def handle_bad_id(e):
    code = 404
    e_type = e.__class__.__name__
    text = e.args[0]
    title = "not found"
    return jsonify(error=code, title=title, error_type=e_type, text=text), code


@app.errorhandler(BadData)
def handle_bad_id(e):
    code = 400
    e_type = e.__class__.__name__
    text = e.args[0]
    title = "bad request"
    return jsonify(error=code, title=title, error_type=e_type, text=text), code


def _get_json() -> dict:
    """
    :raise: BadRequest
    :rtype: dict
    :return: JSON as dict
    """
    try:
        return request.get_json()
    except BadRequest:
        msg = "This here is we call a fucked-up JSON: {}".format(request.data)
        raise BadRequest(msg)


def _get_method():
    method = request.method
    if method == 'HEAD':
        return 'GET'
    return method


if __name__ == '__main__':
    app.run(port=5000)
