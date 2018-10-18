from typing import Optional

from zoo_keeper_server.zoo_service_request_handler import ZooServiceRequestHandler


class Validator(object):
    def __init__(self, zoo_service_url):
        self.zoo_service_rh = ZooServiceRequestHandler(zoo_service_url)

    def is_zoo_ok(self, zoo_id: Optional[int]):
        if zoo_id is None:
            return True
        return self.zoo_service_rh.has_zoo(zoo_id)

    def is_favorite_monkey_ok(self, monkey_id: Optional[int], zoo_id: Optional[int]):
        if monkey_id is None:
            return True
        if zoo_id is None:
            return False
        return (self.zoo_service_rh.has_monkey(monkey_id) and
                self.zoo_service_rh.is_monkey_in_zoo(monkey_id, zoo_id))

    def is_dream_monkey_ok(self, monkey_id: Optional[int], zoo_id: Optional[int]):
        if monkey_id is None:
            return True
        if zoo_id is None:
            return False
        return (self.zoo_service_rh.has_monkey(monkey_id) and
                not self.zoo_service_rh.is_monkey_in_zoo(monkey_id, zoo_id))

    def raise_value_errors(self, zoo_id, favorite_monkey_id, dream_monkey_id):
        if not self.is_zoo_ok(zoo_id):
            raise ValueError('zoo: "{}" does not exists'.format(zoo_id))
        if not self.is_favorite_monkey_ok(favorite_monkey_id, zoo_id):
            raise ValueError('monkey: "{}" does not exist or is not in zoo: "{}"'.format(favorite_monkey_id, zoo_id))
        if not self.is_dream_monkey_ok(dream_monkey_id, zoo_id):
            raise ValueError('monkey: "{}" does not exist or IS in zoo: "{}"'.format(dream_monkey_id, zoo_id))
