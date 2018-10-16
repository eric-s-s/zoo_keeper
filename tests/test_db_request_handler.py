import json
import unittest
from unittest.mock import patch

import requests

import tests.create_test_data as test_data

from zoo_keeper_server.db_request_handler import DBRequestHandler, BadId, BadData
from zoo_keeper_server.zoo_service_request_handler import NoResponse, BadResponse

from tests.mock_requests import MockRequests

REQUESTS_GET_PATCH = 'requests.get'
REQUESTS_HEAD_PATCH = 'requests.head'


class TestDBRequestHandler(unittest.TestCase):

    def setUp(self):
        self.session = test_data.TestSession()
        self.handler = DBRequestHandler(self.session)
        test_data.create_all_test_data(self.session)
        self.maxDiff = None

    def tearDown(self):
        self.session.close()

    @patch("requests.get", MockRequests.get)
    def test_get_all_monkeys(self):
        answer = self.handler.get_all_monkeys()

        expected = [
            {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1},
            {'id': 2, 'name': 'b', 'sex': 'f', 'flings_poop': 'TRUE', 'poop_size': 2, 'zoo_id': 1},
            {'id': 3, 'name': 'a', 'sex': 'm', 'flings_poop': 'FALSE', 'poop_size': 3, 'zoo_id': 2},
            {'id': 4, 'name': 'a', 'sex': 'f', 'flings_poop': 'FALSE', 'poop_size': 4, 'zoo_id': 2}
        ]

        self.assertEqual(json.loads(answer[0]), expected)
        self.assertEqual(answer[1], 200)

    @patch('requests.get', MockRequests.get)
    def test_get_all_zoos(self):
        answer = self.handler.get_all_zoos()

        expected = [
            {'id': 1,
             'name': 'a',
             'opens': '12:00',
             'closes': '13:00',
             'monkeys': [
                 {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1},
                 {'id': 2, 'name': 'b', 'sex': 'f', 'flings_poop': 'TRUE', 'poop_size': 2, 'zoo_id': 1}
             ]},
            {'id': 2,
             'name': 'b',
             'opens': '14:00',
             'closes': '15:00',
             'monkeys': [
                 {'id': 3, 'name': 'a', 'sex': 'm', 'flings_poop': 'FALSE', 'poop_size': 3, 'zoo_id': 2},
                 {'id': 4, 'name': 'a', 'sex': 'f', 'flings_poop': 'FALSE', 'poop_size': 4, 'zoo_id': 2}
             ]}
        ]

        self.assertEqual(json.loads(answer[0]), expected)
        self.assertEqual(answer[1], 200)

    @patch("requests.get", MockRequests.get)
    def test_get_all_zoo_keepers(self):
        response = self.handler.get_all_zoo_keepers()
        response_json = json.loads(response[0])

        expected = [
            {'id': 1,
             'age': 10,
             'dream_monkey': {
                 'flings_poop': 'FALSE', 'id': 3, 'name': 'a', 'poop_size': 3, 'sex': 'm', 'zoo_id': 2
             },
             'dream_monkey_id': 3,
             'favorite_monkey': {
                 'flings_poop': 'TRUE', 'id': 1, 'name': 'a', 'poop_size': 1, 'sex': 'm', 'zoo_id': 1
             },
             'favorite_monkey_id': 1,
             'name': 'a',
             'zoo': {
                 'closes': '13:00', 'id': 1,
                 'monkeys': [
                     {'flings_poop': 'TRUE', 'id': 1, 'name': 'a', 'poop_size': 1, 'sex': 'm', 'zoo_id': 1},
                     {'flings_poop': 'TRUE', 'id': 2, 'name': 'b', 'poop_size': 2, 'sex': 'f', 'zoo_id': 1}
                 ],
                 'name': 'a',
                 'opens': '12:00'
             },
             'zoo_id': 1
             },
            {'id': 2,
             'age': 20,
             'dream_monkey': {},
             'dream_monkey_id': None,
             'favorite_monkey': {
                 'flings_poop': 'FALSE', 'id': 3, 'name': 'a', 'poop_size': 3, 'sex': 'm', 'zoo_id': 2
             },
             'favorite_monkey_id': 3,
             'name': 'b',
             'zoo': {
                 'closes': '15:00',
                 'id': 2, 'monkeys': [
                    {'flings_poop': 'FALSE', 'id': 3, 'name': 'a', 'poop_size': 3, 'sex': 'm', 'zoo_id': 2},
                    {'flings_poop': 'FALSE', 'id': 4, 'name': 'a', 'poop_size': 4, 'sex': 'f', 'zoo_id': 2}
                 ],
                 'name': 'b',
                 'opens': '14:00'
             },
             'zoo_id': 2
             },
            {'id': 3,
             'age': 30,
             'dream_monkey': {},
             'dream_monkey_id': None,
             'favorite_monkey': {},
             'favorite_monkey_id': None,
             'name': 'c',
             'zoo': {
                 'closes': '15:00',
                 'id': 2,
                 'monkeys': [
                     {'flings_poop': 'FALSE', 'id': 3, 'name': 'a', 'poop_size': 3, 'sex': 'm', 'zoo_id': 2},
                     {'flings_poop': 'FALSE', 'id': 4, 'name': 'a', 'poop_size': 4, 'sex': 'f', 'zoo_id': 2}
                 ],
                 'name': 'b',
                 'opens': '14:00'
             },
             'zoo_id': 2
             },
            {'id': 4,
             'age': 40,
             'dream_monkey': {},
             'dream_monkey_id': None,
             'favorite_monkey': {},
             'favorite_monkey_id': None,
             'name': 'd',
             'zoo': {},
             'zoo_id': None
             }
        ]
        self.assertEqual(response_json, expected)
        self.assertEqual(response[1], 200)

    @patch('requests.get', MockRequests.get)
    def test_get_zoo_keeper_correct(self):
        response = self.handler.get_zoo_keeper(1)
        response_json = json.loads(response[0])
        expected = {
            'id': 1,
            'age': 10,
            'dream_monkey': {
                'flings_poop': 'FALSE', 'id': 3, 'name': 'a', 'poop_size': 3, 'sex': 'm', 'zoo_id': 2
            },
            'dream_monkey_id': 3,
            'favorite_monkey': {
                'flings_poop': 'TRUE', 'id': 1, 'name': 'a', 'poop_size': 1, 'sex': 'm', 'zoo_id': 1},
            'favorite_monkey_id': 1,
            'name': 'a',
            'zoo': {
                'closes': '13:00',
                'id': 1,
                'monkeys': [
                    {'flings_poop': 'TRUE', 'id': 1, 'name': 'a', 'poop_size': 1, 'sex': 'm', 'zoo_id': 1},
                    {'flings_poop': 'TRUE', 'id': 2, 'name': 'b', 'poop_size': 2, 'sex': 'f', 'zoo_id': 1}
                ],
                'name': 'a',
                'opens': '12:00'
            },
            'zoo_id': 1
        }
        self.assertEqual(expected, response_json)
        self.assertEqual(response[1], 200)

        response = self.handler.get_zoo_keeper(4)
        response_json = json.loads(response[0])
        expected = {
            'id': 4,
            'age': 40,
            'dream_monkey': {},
            'dream_monkey_id': None,
            'favorite_monkey': {},
            'favorite_monkey_id': None,
            'name': 'd',
            'zoo': {},
            'zoo_id': None
        }
        self.assertEqual(expected, response_json)
        self.assertEqual(response[1], 200)

    @patch('requests.get', MockRequests.get)
    def test_get_zoo_keeper_bad_id(self):
        self.assertRaises(BadId, self.handler.get_zoo_keeper, 1000)

    @patch('requests.get', MockRequests.get)
    def test_post_zoo_keeper_minimum_fields(self):
        to_post = {'name': 'e', 'age': 50}
        first_answer = self.handler.post_zoo_keeper(to_post)
        first_answer_json = json.loads(first_answer[0])

        expected = {'age': 50,
                    'dream_monkey': {},
                    'dream_monkey_id': None,
                    'favorite_monkey': {},
                    'favorite_monkey_id': None,
                    'name': 'e',
                    'zoo': {},
                    'zoo_id': None,
                    'id': first_answer_json['id']
                    }

        self.assertEqual(expected, first_answer_json)
        self.assertEqual(first_answer[1], 200)

        second_answer = self.handler.get_zoo_keeper(expected['id'])
        self.assertEqual(first_answer, second_answer)

    @patch('requests.get', MockRequests.get)
    def test_post_zoo_keeper_all_fields(self):
        to_post = {
            'name': 'e', 'age': 50, 'zoo_id': 1, 'favorite_monkey_id': 1, 'dream_monkey_id': 3
        }
        response = self.handler.post_zoo_keeper(to_post)
        response_json = json.loads(response[0])
        expected = {
            'age': 50,
            'dream_monkey': {
                'flings_poop': 'FALSE',
                'id': 3,
                'name': 'a',
                'poop_size': 3,
                'sex': 'm',
                'zoo_id': 2
            },
            'dream_monkey_id': 3,
            'favorite_monkey': {
                'flings_poop': 'TRUE',
                'id': 1,
                'name': 'a',
                'poop_size': 1,
                'sex': 'm',
                'zoo_id': 1
            },
            'favorite_monkey_id': 1,
            'id': response_json['id'],
            'name': 'e',
            'zoo': {
                'closes': '13:00',
                'id': 1,
                'monkeys': [
                    {'flings_poop': 'TRUE',
                     'id': 1,
                     'name': 'a',
                     'poop_size': 1,
                     'sex': 'm',
                     'zoo_id': 1},
                    {'flings_poop': 'TRUE',
                     'id': 2,
                     'name': 'b',
                     'poop_size': 2,
                     'sex': 'f',
                     'zoo_id': 1}
                ],
                'name': 'a',
                'opens': '12:00'
            },
            'zoo_id': 1}
        self.assertEqual(response_json, expected)
        self.assertEqual(response[1], 200)

        get_response = self.handler.get_zoo_keeper(response_json['id'])
        self.assertEqual(get_response, response)

    @patch('requests.get', MockRequests.get)
    def test_post_zoo_keeper_bad_data(self):

        to_post = {'oops': 1}
        self.assertRaises(BadData, self.handler.post_zoo_keeper, to_post)

        to_post = {'oops': 1, 'name': 'd', 'age': 10}
        self.assertRaises(BadData, self.handler.post_zoo_keeper, to_post)

        to_post = {'oops': 1, 'name': 'd', 'age': 10, 'zoo_id': 1,
                   'favorite_monkey_id': 1, 'dream_monkey_id': 3}
        self.assertRaises(BadData, self.handler.post_zoo_keeper, to_post)

        to_post = {'name': 'd'}
        self.assertRaises(BadData, self.handler.post_zoo_keeper, to_post)

    @patch('requests.get', MockRequests.get)
    def test_put_zoo_keeper_all_fields(self):
        to_put_id = 4
        to_put = {
            'name': 'e', 'age': 50, 'zoo_id': 1, 'favorite_monkey_id': 1, 'dream_monkey_id': 3
        }
        response = self.handler.put_zoo_keeper(to_put_id, to_put)
        response_json = json.loads(response[0])
        expected = {
            'age': 50,
            'dream_monkey': {
                'flings_poop': 'FALSE',
                'id': 3,
                'name': 'a',
                'poop_size': 3,
                'sex': 'm',
                'zoo_id': 2
            },
            'dream_monkey_id': 3,
            'favorite_monkey': {
                'flings_poop': 'TRUE',
                'id': 1,
                'name': 'a',
                'poop_size': 1,
                'sex': 'm',
                'zoo_id': 1
            },
            'favorite_monkey_id': 1,
            'id': to_put_id,
            'name': 'e',
            'zoo': {
                'closes': '13:00',
                'id': 1,
                'monkeys': [
                    {'flings_poop': 'TRUE',
                     'id': 1,
                     'name': 'a',
                     'poop_size': 1,
                     'sex': 'm',
                     'zoo_id': 1},
                    {'flings_poop': 'TRUE',
                     'id': 2,
                     'name': 'b',
                     'poop_size': 2,
                     'sex': 'f',
                     'zoo_id': 1}
                ],
                'name': 'a',
                'opens': '12:00'
            },
            'zoo_id': 1}
        self.assertEqual(response_json, expected)
        self.assertEqual(response[1], 200)

        get_response = self.handler.get_zoo_keeper(to_put_id)
        self.assertEqual(get_response, response)

    @patch('requests.get', MockRequests.get)
    def test_put_zoo_keeper_partial(self):
        to_put_id = 4
        to_put = {"zoo_id": 1, "name": "new"}

        current_state = json.loads(self.handler.get_zoo_keeper(to_put_id)[0])
        expected = {
            'age': 40,
            'dream_monkey': {},
            'dream_monkey_id': None,
            'favorite_monkey': {},
            'favorite_monkey_id': None,
            'id': 4,
            'name': 'new',
            'zoo': {
                'closes': '13:00',
                'id': 1,
                'monkeys': [
                    {'flings_poop': 'TRUE', 'id': 1, 'name': 'a', 'poop_size': 1, 'sex': 'm', 'zoo_id': 1},
                    {'flings_poop': 'TRUE', 'id': 2, 'name': 'b', 'poop_size': 2, 'sex': 'f', 'zoo_id': 1}
                ], 'name': 'a',
                'opens': '12:00'
            },
            'zoo_id': 1
        }
        self.assertNotEqual(current_state, expected)

        response = self.handler.put_zoo_keeper(to_put_id, to_put)
        self.assertEqual(json.loads(response[0]), expected)
        self.assertEqual(response[1], 200)

        get_response = self.handler.get_zoo_keeper(to_put_id)
        self.assertEqual(get_response, response)

    @patch('requests.get', MockRequests.get)
    def test_put_zoo_keeper_bad_id(self):
        self.assertRaises(BadId, self.handler.put_zoo_keeper, 1000, {})

    @patch('requests.get', MockRequests.get)
    def test_put_zoo_keeper_bad_data(self):

        to_put = {'oops': 1}
        self.assertRaises(BadData, self.handler.put_zoo_keeper, 1, to_put)

        to_put = {'oops': 1, 'name': 'd', 'age': 10}
        self.assertRaises(BadData, self.handler.put_zoo_keeper, 1, to_put)

        to_put = {'oops': 1, 'name': 'd', 'age': 10, 'zoo_id': 1,
                  'favorite_monkey_id': 1, 'dream_monkey_id': 3}
        self.assertRaises(BadData, self.handler.put_zoo_keeper, 1, to_put)

    @patch('requests.get', MockRequests.get)
    def test_delete_zoo_keeper(self):
        current_zoo_keepers = json.loads(self.handler.get_all_zoo_keepers()[0])
        response = self.handler.delete_zoo_keeper(1)
        self.assertNotEqual(json.loads(response[0]), current_zoo_keepers)
        del current_zoo_keepers[0]
        self.assertEqual(json.loads(response[0]), current_zoo_keepers)
        self.assertEqual(response[1], 200)

        self.assertRaises(BadId, self.handler.get_zoo_keeper, 1)

    @patch('requests.get', MockRequests.get)
    def test_delete_zoo_keeper_bad_id(self):
        self.assertRaises(BadId, self.handler.delete_zoo_keeper, 100)

    @patch('requests.get')
    def test_zoo_service_no_response(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()

        response = self.handler.get_zoo_keeper(3)
        response_json = json.loads(response[0])
        expected = {
            'id': 3,
            'age': 30,
            'dream_monkey': {},
            'dream_monkey_id': None,
            'favorite_monkey': {},
            'favorite_monkey_id': None,
            'name': 'c',
            'zoo': {
                'error': 504,
                'error_type': 'NoResponse',
                'text': 'at address: http://localhost:8080/zoos/2, attempts: 3, timeout after: 2 seconds',
                'title': 'gateway timeout'
            },
            'zoo_id': 2}
        self.assertEqual(expected, response_json)
        self.assertEqual(response[1], 200)

    @patch('requests.get', MockRequests.get)
    def test_zoo_service_bad_id(self):
        response = self.handler.post_zoo_keeper({'name': 'e', 'age': 50, 'zoo_id': 100})
        response_json = json.loads(response[0])
        expected = {
            'age': 50,
            'dream_monkey': {},
            'dream_monkey_id': None,
            'favorite_monkey': {},
            'favorite_monkey_id': None,
            'id': response_json['id'],
            'name': 'e',
            'zoo': {
                'error': 404,
                'error_type': 'BadId',
                'text': response_json['zoo']['text'],
                'title': 'not found'
            },
            'zoo_id': 100
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response[1], 200)

