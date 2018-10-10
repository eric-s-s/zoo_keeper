from functools import partial

from flask import Flask, request
from werkzeug.exceptions import BadRequest

from zoo_keeper_server.db_request_handler import safe_handler, DBRequestHandler


app = Flask(__name__)


@app.route('/zoos/', methods=['GET'])
def all_zoos():
    with safe_handler() as handler:  # type: DBRequestHandler
        return handler.get_all_zoos()


@app.route('/monkeys/', methods=['GET'])
def all_monkeys():
    with safe_handler() as handler:  # type: DBRequestHandler
        return handler.get_all_zoos()


@app.route('/zoo_keepers/', methods=['GET', 'POST'])
def all_zoo_keepers():
    with safe_handler() as handler:  # type: DBRequestHandler
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
    with safe_handler() as handler:  # type: DBRequestHandler
        method = _get_method()

        request_json = _get_json()

        actions = {
            'GET': partial(handler.get_zoo_keeper, zoo_keeper_id),
            'PUT': partial(handler.put_zoo_keeper, zoo_keeper_id, request_json),
            'DELETE': partial(handler.delete_zoo_keeper, zoo_keeper_id)
        }
        reply = actions[method]()
    return reply


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
