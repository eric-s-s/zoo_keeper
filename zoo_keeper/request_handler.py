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

    def get_all_zoo_keepers(self):
        zoo_keepers = self.session.query(ZooKeeper).all()
        all_jsons = [self._get_keeper_json(keeper) for keeper in zoo_keepers]
        return json.dumps(all_jsons), 200

    def get_single_zookeeper(self, keeper_name):
        zoo_keeper = self.session.query(ZooKeeper).filter(ZooKeeper.name == keeper_name).first()
        if zoo_keeper is None:
            return "zoo keeper: {} does not exists".format(keeper_name), 404
        keeper_json = self._get_keeper_json(zoo_keeper)
        return json.dumps(keeper_json), 200

    def _get_keeper_json(self, zoo_keeper: ZooKeeper) -> dict:
        keeper_dict = zoo_keeper.to_dict()
        del keeper_dict['zoo_name']

        keeper_dict['zoo'] = self.server_request.get_single_zoo(zoo_keeper.zoo_name)
        keeper_dict['dream_monkey'] = self.server_request.get_single_monkey(zoo_keeper.dream_monkey)
        keeper_dict['favorite_monkey'] = self.server_request.get_single_monkey(zoo_keeper.favorite_monkey)

        return keeper_dict

    def post_zoo_keeper(self, json_data):
        kwargs = _convert_json(json_data)
        try:
            new_keeper = ZooKeeper(**kwargs)
        except ValueError as error:
            return error.args[0], 400
        self.session.add(new_keeper)
        self.session.commit()
        return self.get_single_zookeeper(new_keeper.name)

    def put_zoo_keeper(self, keeper_name, json_data):
        keeper = self.session.query(ZooKeeper).filter(ZooKeeper.name == keeper_name).first()  # type: ZooKeeper
        if keeper is None:
            return 'zoo keeper: {} does not exists'.format(keeper_name), 404
        kwargs = _convert_json(json_data)
        try:
            keeper.set_attributes(**kwargs)
        except ValueError as error:
            return error.args[0], 400

        self.session.commit()
        return self.get_single_zookeeper(keeper.name)

    def delete_all_zoo_keepers(self):
        all_keepers = self.session.query(ZooKeeper).all()
        for keeper in all_keepers:
            self.session.delete(keeper)
        self.session.commit()
        return self.get_all_zoo_keepers()

    def delete_single_zoo_keeper(self, keeper_name):
        keeper = self.session.query(ZooKeeper).filter(ZooKeeper.name == keeper_name).first()
        if keeper is None:
            return "zoo keeper: {} does not exist".format(keeper_name), 404
        self.session.delete(keeper)
        return self.get_all_zoo_keepers()

    def close_connection(self):
        self.session.close()


def _get_code(json_obj):
    if not json_obj:
        return 404
    return 200


def _convert_json(json_data):
    return {key: _convert_value(value) for key, value in json_data.items()}


def _convert_value(json_value_str):
    if json_value_str.lower() in ('none', 'null'):
        return None
    try:
        return int(json_value_str)
    except ValueError:
        return json_value_str


@contextmanager
def safe_handler():
    handler = RequestHandler()
    try:
        yield handler
    finally:
        handler.close_connection()


if __name__ == '__main__':
    # pseudo tests
    with safe_handler() as sh:  # type: RequestHandler
        print(sh.get_single_zookeeper('oops'))
