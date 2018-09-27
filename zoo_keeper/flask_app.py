import requests
from functools import partial

from flask import Flask, request
from werkzeug.exceptions import BadRequest


app = Flask(__name__)


@app.route('/zoos/', methods=['GET'])
def all_zoos():

    r = requests.get('http://localhost:8080/zoos/')

    return r.content, r.status_code


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
