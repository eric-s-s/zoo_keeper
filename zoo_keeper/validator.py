from zoo_keeper.server_requests import ServerRequests


class Validator(object):
    def __init__(self):
        self.to_server = ServerRequests()
        self.sr = ServerRequests()

    def is_zoo_ok(self, zoo_name):
        if zoo_name is None:
            return True
        return self.sr.has_zoo(zoo_name)

    def is_favorite_monkey_ok(self, monkey_id, zoo_name):
        if monkey_id is None:
            return True
        if zoo_name is None:
            return False
        return self.sr.has_monkey(monkey_id) and self.sr.is_monkey_in_zoo(monkey_id, zoo_name)

    def is_dream_monkey_ok(self, monkey_id, zoo_name):
        if monkey_id is None:
            return True
        if zoo_name is None:
            return False
        return self.sr.has_monkey(monkey_id) and not self.sr.is_monkey_in_zoo(monkey_id, zoo_name)

    def raise_value_errors(self, zoo_name, favorite_monkey, dream_monkey):
        if not self.is_zoo_ok(zoo_name):
            raise ValueError('zoo: "{}" does not exists'.format(zoo_name))
        if not self.is_favorite_monkey_ok(favorite_monkey, zoo_name):
            raise ValueError('monkey: "{}" does not exist or is not in zoo: "{}"'.format(favorite_monkey, zoo_name))
        if not self.is_dream_monkey_ok(dream_monkey, zoo_name):
            raise ValueError('monkey: "{}" does not exist or is not in zoo: "{}"'.format(dream_monkey, zoo_name))
