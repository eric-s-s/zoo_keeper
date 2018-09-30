from contextlib import contextmanager
import json

from zoo_keeper.zoo_keeper_class import ZooKeeper
from zoo_keeper.server_requests import ServerRequests
from zoo_keeper.session import Session


class RequestHandler(object):
    def __init__(self):
        self.session = Session()
        self.server_request = ServerRequests()

    def get_all_zoos(self):
        response = self.server_request.get_all_zoos()
        response_code = _get_code(response)
        return json.dumps(response), response_code

    def get_all_monkeys(self):
        response = self.server_request.get_all_monkeys()
        response_code = _get_code(response)
        return json.dumps(response), response_code

    def get_all_zookeepers(self):
        zoo_keepers = self.session.query(ZooKeeper).all()
        for keeper in zoo_keepers:
            keeper.se

    def _get_details(self, zoo_keeper_dict):
        pass

    def close_connection(self):
        self.session.close()


def _get_code(json_obj):
    if not json_obj:
        return 404
    return 200


@contextmanager
def safe_handler():
    handler = RequestHandler()
    try:
        yield handler
    finally:
        handler.close_connection()