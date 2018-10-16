import requests
import json

from zoo_keeper_server import SERVER_URL


class BadResponse(ValueError):
    pass


class NoResponse(TimeoutError):
    pass


class ZooServiceRequestHandler(object):
    def __init__(self, server_url=SERVER_URL, timeout=2, request_attempts=3):
        self.server_url = server_url
        self.zoo_addr = '{}/zoos/'.format(self.server_url)
        self.monkey_addr = '{}/monkeys/'.format(self.server_url)
        self.timeout = timeout
        self.request_attempts = request_attempts

    def handle_request(self, address, use_get=True):
        tries = 0
        if use_get:
            requests_method = requests.get
        else:
            requests_method = requests.head

        while tries < self.request_attempts:
            try:
                return requests_method(address, timeout=self.timeout)
            except requests.exceptions.Timeout:
                tries += 1
        info = {"retries": self.request_attempts, "timeout": self.timeout, "address": address}
        raise NoResponse(json.dumps(info))

    def get_all_monkeys(self) -> dict:
        request = self.handle_request(self.monkey_addr)
        _check_response(request)
        return request.json()

    def get_all_zoos(self) -> dict:
        request = self.handle_request(self.zoo_addr)
        _check_response(request)
        return request.json()

    def get_monkey(self, monkey_id: int) -> dict:
        request = self.handle_request(self.monkey_addr + str(monkey_id))
        _check_response(request)
        return request.json()

    def get_zoo(self, zoo_id: int) -> dict:
        request = self.handle_request(self.zoo_addr + str(zoo_id))
        _check_response(request)
        return request.json()

    def has_zoo(self, zoo_id: int) -> bool:
        request = self.handle_request(self.zoo_addr + str(zoo_id), use_get=False)
        return request.ok

    def has_monkey(self, monkey_id: int) -> bool:
        request = self.handle_request(self.monkey_addr + str(monkey_id), use_get=False)
        return request.ok

    def is_monkey_in_zoo(self, monkey_id: int, zoo_id: int) -> bool:
        request = self.handle_request(self.monkey_addr + str(monkey_id))
        _check_response(request)
        test_json = request.json()
        return test_json['zoo_id'] == zoo_id


def _check_response(request: requests.models.Response):
    if not request.ok:
        raise BadResponse(request.json())


if __name__ == '__main__':
    """
    here be pseudo-tests.
    """
    zoo = 2
    sr = ZooServiceRequestHandler()
    from pprint import pprint
    pprint(sr.get_all_monkeys())
    pprint(sr.get_all_zoos())
    pprint(sr.get_monkey(1))
    pprint(sr.get_zoo(zoo))
    pprint(sr.get_zoo_from_monkey_id(1))
    print(sr.has_zoo(zoo))
    print(sr.has_zoo('no'))
    print(sr.has_monkey(1))
    print(sr.has_monkey(10))
    print(sr.is_monkey_in_zoo(1, "nope"))
    print(sr.is_monkey_in_zoo(2, zoo))

    print(sr.get_monkey(None))

    print(sr.get_zoo(None))
    print(sr.get_zoo_from_monkey_id(None))
