import requests
import json


class BadResponse(ValueError):
    pass


class NoResponse(TimeoutError):
    pass


class ZooServiceRequestHandler(object):
    def __init__(self, zoo_service_url, timeout=2, request_attempts=3):
        self.server_url = zoo_service_url
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

        error_text = ""
        while tries < self.request_attempts:
            try:
                return requests_method(address, timeout=self.timeout)
            except requests.exceptions.Timeout:
                tries += 1
            except requests.exceptions.ConnectionError as e:
                error_text = str(e)
                break
        if not error_text:
            error_text = "at address: {}, attempts: {}, timeout after: {} seconds".format(
                address, self.request_attempts, self.timeout
            )
        info = {
            "error": 504,
            "title": "gateway timeout",
            "error_type": "NoResponse",
            "text": error_text
        }
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
        raise BadResponse(json.dumps(request.json()))
