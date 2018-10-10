from contextlib import contextmanager
import json

from zoo_keeper_server.zoo_keeper_class import ZooKeeper
from zoo_keeper_server.zoo_service_request_handler import ZooServiceRequestHandler
from zoo_keeper_server.session import create_session


class DBRequestHandler(object):
    def __init__(self, host='localhost'):
        self.session = create_session(host)
        self.zoo_service_rh = ZooServiceRequestHandler()

    def get_all_zoos(self):
        response = self.zoo_service_rh.get_all_zoos()
        response_code = _get_code(response)
        return json.dumps(response), response_code

    def get_all_monkeys(self):
        response = self.zoo_service_rh.get_all_monkeys()
        response_code = _get_code(response)
        return json.dumps(response), response_code

    def get_all_zoo_keepers(self):
        zoo_keepers = self.session.query(ZooKeeper).all()
        all_jsons = [self._get_zoo_keeper_json(keeper) for keeper in zoo_keepers]
        return json.dumps(all_jsons), 200

    def get_zoo_keeper(self, zoo_keeper_id):
        zoo_keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()
        if zoo_keeper is None:
            return "zoo keeper: {} does not exists".format(zoo_keeper_id), 404
        zoo_keeper_json = self._get_zoo_keeper_json(zoo_keeper)
        return json.dumps(zoo_keeper_json), 200

    def _get_zoo_keeper_json(self, zoo_keeper: ZooKeeper) -> dict:
        output_json = zoo_keeper.to_dict()

        output_json['zoo'] = self.zoo_service_rh.get_zoo(zoo_keeper.zoo_id)
        output_json['dream_monkey'] = self.zoo_service_rh.get_monkey(zoo_keeper.dream_monkey_id)
        output_json['favorite_monkey'] = self.zoo_service_rh.get_monkey(zoo_keeper.favorite_monkey_id)

        return output_json

    def post_zoo_keeper(self, json_data):
        kwargs = _convert_json(json_data)
        try:
            new_keeper = ZooKeeper(**kwargs)
        except ValueError as error:
            return error.args[0], 400
        self.session.add(new_keeper)
        self.session.commit()
        return self.get_zoo_keeper(new_keeper.id)

    def put_zoo_keeper(self, zoo_keeper_id, json_data):
        keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()  # type: ZooKeeper
        if keeper is None:
            return 'zoo keeper: {} does not exists'.format(zoo_keeper_id), 404
        kwargs = _convert_json(json_data)
        try:
            keeper.set_attributes(**kwargs)
        except ValueError as error:
            return error.args[0], 400

        self.session.commit()
        return self.get_zoo_keeper(keeper.id)

    def delete_zoo_keeper(self, zoo_keeper_id):
        keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()
        if keeper is None:
            return "zoo keeper: {} does not exist".format(zoo_keeper_id), 404
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
    handler = DBRequestHandler()
    try:
        yield handler
    finally:
        handler.close_connection()


if __name__ == '__main__':
    # pseudo tests
    with safe_handler() as sh:  # type: DBRequestHandler
        print(sh.get_zoo_keeper(1))
