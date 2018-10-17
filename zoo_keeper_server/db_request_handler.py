import json

from zoo_keeper_server.zoo_keeper import ZooKeeper
from zoo_keeper_server.zoo_service_request_handler import ZooServiceRequestHandler, NoResponse, BadResponse


class BadId(ValueError):
    pass


class BadData(ValueError):
    pass


class DBRequestHandler(object):
    def __init__(self, session):
        self.session = session
        self.zoo_service_rh = ZooServiceRequestHandler()
        self.zoo_keeper_keys = {
            "name", "age", "zoo_id", "favorite_monkey_id", "dream_monkey_id"
        }
        self.minimum_zoo_keeper_keys = {'name', 'age'}

    def get_all_zoos(self):
        try:
            response = self.zoo_service_rh.get_all_zoos()
            response_code = 200
        except NoResponse as e:
            response = json.loads(e.args[0])
            response_code = 504
        return json.dumps(response), response_code

    def get_all_monkeys(self):
        try:
            response = self.zoo_service_rh.get_all_monkeys()
            response_code = 200
        except NoResponse as e:
            response = json.loads(e.args[0])
            response_code = 504
        return json.dumps(response), response_code

    def get_all_zoo_keepers(self):
        zoo_keepers = self.session.query(ZooKeeper).all()
        all_jsons = [self._get_zoo_keeper_json(zoo_keeper) for zoo_keeper in zoo_keepers]
        return json.dumps(all_jsons), 200

    def get_zoo_keeper(self, zoo_keeper_id):
        zoo_keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()
        _raise_bad_id_for_none_value(zoo_keeper, zoo_keeper_id)
        zoo_keeper_json = self._get_zoo_keeper_json(zoo_keeper)
        return json.dumps(zoo_keeper_json), 200

    def _get_zoo_keeper_json(self, zoo_keeper: ZooKeeper) -> dict:
        output_json = zoo_keeper.to_dict()
        keys_to_methods = {
            'zoo': self.zoo_service_rh.get_zoo,
            'dream_monkey': self.zoo_service_rh.get_monkey,
            'favorite_monkey': self.zoo_service_rh.get_monkey
        }
        for key, method in keys_to_methods.items():
            zoo_service_id = getattr(zoo_keeper, key + '_id')
            if zoo_service_id is None:
                json_data = {}
            else:
                try:
                    json_data = method(zoo_service_id)
                except (BadResponse, NoResponse) as e:
                    json_data = json.loads(e.args[0])
            output_json[key] = json_data
        return output_json

    def post_zoo_keeper(self, json_data):
        self._raise_bad_data_post(json_data)
        kwargs = _convert_json(json_data)
        new_zoo_keeper = ZooKeeper(**kwargs)
        self.session.add(new_zoo_keeper)
        self.session.commit()
        return self.get_zoo_keeper(new_zoo_keeper.id)

    def put_zoo_keeper(self, zoo_keeper_id, json_data):
        self._raise_bad_data_put(json_data)
        zoo_keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()  # type: ZooKeeper
        _raise_bad_id_for_none_value(zoo_keeper, zoo_keeper_id)
        kwargs = _convert_json(json_data)
        zoo_keeper.set_attributes(**kwargs)

        self.session.commit()
        return self.get_zoo_keeper(zoo_keeper.id)

    def _raise_bad_data_post(self, json_data):
        json_data_keys = set(json_data.keys())
        if not self.minimum_zoo_keeper_keys <= json_data_keys <= self.zoo_keeper_keys:
            msg = "json keys: {}. minimum keys: {}. maximum keys: {}"
            msg = msg.format(json_data_keys, self.minimum_zoo_keeper_keys, self.zoo_keeper_keys)
            raise BadData(msg)

    def _raise_bad_data_put(self, json_data):
        json_data_keys = set(json_data.keys())
        if not json_data_keys.issubset(self.zoo_keeper_keys):
            msg = "json keys: {} must be subset of {}".format(json_data_keys, self.zoo_keeper_keys)
            raise BadData(msg)

    def delete_zoo_keeper(self, zoo_keeper_id):
        zoo_keeper = self.session.query(ZooKeeper).filter(ZooKeeper.id == zoo_keeper_id).first()
        _raise_bad_id_for_none_value(zoo_keeper, zoo_keeper_id)
        self.session.delete(zoo_keeper)
        return self.get_all_zoo_keepers()


def _get_code(json_obj):
    if not json_obj:
        return 404
    return 200


def _convert_json(json_data):
    return {key: _convert_value(value) for key, value in json_data.items()}


def _convert_value(value):
    if not isinstance(value, str):
        return value
    if value.lower() in ('none', 'null'):
        return None

    try:
        return int(value)
    except ValueError:
        return value


def _raise_bad_id_for_none_value(response_obj, id_value):
    if response_obj is None:
        raise BadId('id does not exist: {}'.format(id_value))


if __name__ == '__main__':
    # pseudo tests
    # with safe_handler() as sh:  # type: DBRequestHandler
    #     print(sh.get_zoo_keeper(1))
    pass
