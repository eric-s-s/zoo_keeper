import time


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    @property
    def ok(self):
        return self.status_code == 200

    def json(self):
        return self.json_data.copy()


class MockRequests(object):
    zoos = {
        1: {'id': 1, 'name': 'a', 'opens': '12:00', 'closes': '13:00', 'monkey_ids': [1, 2]},
        2: {'id': 2, 'name': 'b', 'opens': '14:00', 'closes': '15:00', 'monkey_ids': [3, 4]}
    }
    monkeys = {
        1: {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1},
        2: {'id': 2, 'name': 'b', 'sex': 'f', 'flings_poop': 'TRUE', 'poop_size': 2, 'zoo_id': 1},
        3: {'id': 3, 'name': 'a', 'sex': 'm', 'flings_poop': 'FALSE', 'poop_size': 3, 'zoo_id': 2},
        4: {'id': 4, 'name': 'a', 'sex': 'f', 'flings_poop': 'FALSE', 'poop_size': 4, 'zoo_id': 2}
    }
    not_found = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': ""
    }

    @classmethod
    def head(cls, addr, timeout=1):
        return cls.get(addr)

    @classmethod
    def get(cls, addr, timeout=1):
        address_parts = addr.split('/')
        if address_parts[-1] == '' and address_parts[-2] == 'zoos':
            return MockResponse(cls.all_zoo_jsons(), 200)
        if address_parts[-1] == '' and address_parts[-2] == 'monkeys':
            return MockResponse(cls.all_monkey_jsons(), 200)

        try:
            id_num = int(address_parts[-1])
        except ValueError:
            return MockResponse(cls.not_found_json(address_parts[-1]), 404)

        if 'zoos' in address_parts:
            json_data = cls.zoo_json(id_num)
        else:
            json_data = cls.monkey_json(id_num)

        status_code = 200
        if 'error' in json_data:
            status_code = 404
        return MockResponse(json_data, status_code)

    @classmethod
    def all_zoo_jsons(cls):
        return [cls.zoo_json(key) for key in cls.zoos.keys()]

    @classmethod
    def all_monkey_jsons(cls):
        return [cls.monkey_json(key) for key in cls.monkeys.keys()]

    @classmethod
    def zoo_json(cls, zoo_id):
        if zoo_id not in cls.zoos.keys():
            return cls.not_found_json(zoo_id)
        to_return = cls.zoos[zoo_id].copy()
        monkey_list = [cls.monkey_json(monkey_id) for monkey_id in to_return['monkey_ids']]
        del to_return['monkey_ids']
        to_return['monkeys'] = monkey_list
        return to_return

    @classmethod
    def monkey_json(cls, monkey_id):
        if monkey_id not in cls.monkeys.keys():
            return cls.not_found_json(monkey_id)
        return cls.monkeys[monkey_id].copy()

    @classmethod
    def not_found_json(cls, id_num):
        to_return = cls.not_found.copy()
        to_return['text'] = "id: {}".format(id_num)
        return to_return
