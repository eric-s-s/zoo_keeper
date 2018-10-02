
import requests

from zoo_keeper import SERVER_URL


class BadUrl(ValueError):
    pass


class ServerRequests(object):
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.zoo_addr = '{}/zoos/'.format(self.server_url)
        self.monkey_addr = '{}/monkeys/'.format(self.server_url)

    def get_all_monkeys(self) -> dict:
        request = requests.get(self.monkey_addr)
        _check_response(request)
        return request.json()

    def get_all_zoos(self) -> dict:
        request = requests.get(self.zoo_addr)
        _check_response(request)
        return request.json()

    def get_single_monkey(self, monkey_id) -> dict:
        if monkey_id is None:
            return {}
        request = requests.get(self.monkey_addr + str(monkey_id))
        _check_response(request)
        return request.json()

    def get_single_zoo(self, zoo_name) -> dict:
        if zoo_name is None:
            return {}
        request = requests.get(self.zoo_addr + zoo_name)
        _check_response(request)
        return request.json()

    def get_zoo_from_monkey_id(self, monkey_id) -> dict:
        if monkey_id is None:
            return {}
        request = requests.get(self.monkey_addr + str(monkey_id) + '/zoo')
        _check_response(request)
        return request.json()

    def has_zoo(self, zoo_name) -> bool:
        request = requests.head(self.zoo_addr + zoo_name)
        return request.ok

    def has_monkey(self, monkey_id) -> bool:
        request = requests.head(self.monkey_addr + str(monkey_id))
        return request.ok

    def is_monkey_in_zoo(self, monkey_id, zoo_name) -> bool:
        if None in (monkey_id, zoo_name):
            return False
        request = requests.get(self.monkey_addr + '{}/zoo/name'.format(monkey_id))
        _check_response(request)
        test_json = request.json()
        return test_json and test_json['name'] == zoo_name


def _check_response(request: requests.models.Response):
    if not request.ok:
        raise BadUrl('response code: {} for url: {}'.format(request.status_code, request.url))


if __name__ == '__main__':
    """
    here be pseudo-tests.
    """
    zoo = "The Boringest Zoo On Earth"
    sr = ServerRequests()
    from pprint import pprint
    pprint(sr.get_all_monkeys())
    pprint(sr.get_all_zoos())
    pprint(sr.get_single_monkey(1))
    pprint(sr.get_single_zoo(zoo))
    pprint(sr.get_zoo_from_monkey_id(1))
    print(sr.has_zoo(zoo))
    print(sr.has_zoo('no'))
    print(sr.has_monkey(1))
    print(sr.has_monkey(10))
    print(sr.is_monkey_in_zoo(1, "nope"))
    print(sr.is_monkey_in_zoo(2, zoo))

    print(sr.get_single_monkey(None))

    print(sr.get_single_zoo(None))
    print(sr.get_zoo_from_monkey_id(None))
