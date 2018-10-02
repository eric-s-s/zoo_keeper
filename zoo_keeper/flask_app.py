from functools import partial

from flask import Flask, request
from werkzeug.exceptions import BadRequest

from zoo_keeper.request_handler import safe_handler, RequestHandler


app = Flask(__name__)


@app.route('/zoos/', methods=['GET'])
def all_zoos():
    with safe_handler() as handler:  # type: RequestHandler
        return handler.get_all_zoos()


@app.route('/monkeys/', methods=['GET'])
def all_monkeys():
    with safe_handler() as handler:  # type: RequestHandler
        return handler.get_all_zoos()


@app.route('/keepers/', methods=['GET', 'POST', 'DELETE'])
def all_keepers():
    with safe_handler() as handler:  # type: RequestHandler
        method = _get_method()

        request_json = _get_json()

        actions = {
            'GET': partial(handler.get_all_zoo_keepers),
            'POST': partial(handler.post_zoo_keeper, request_json),
            'DELETE': partial(handler.delete_all_zoo_keepers)
        }
        reply = actions[method]()
    return reply


@app.route('/keepers/<keeper_name>', methods=['GET', 'PUT', 'DELETE'])
def single_keeper(keeper_name):
    with safe_handler() as handler:  # type: RequestHandler
        method = _get_method()

        request_json = _get_json()

        actions = {
            'GET': partial(handler.get_single_zookeeper, keeper_name),
            'PUT': partial(handler.put_zoo_keeper, keeper_name, request_json),
            'DELETE': partial(handler.delete_single_zoo_keeper, keeper_name)
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
