import unittest
from unittest.mock import patch, call

import json

import requests
import responses

from zoo_keeper_server.zoo_service_request_handler import ZooServiceRequestHandler, NoResponse, BadResponse
from zoo_keeper_server import SERVER_URL
from tests.mock_requests import MockRequests

REQUESTS_GET_PATCH = 'requests.get'
REQUESTS_HEAD_PATCH = 'requests.head'


def callback(request):
    url = request.url
    mock_response = MockRequests.get(url)
    header = {}
    return mock_response.status_code, header, json.dumps(mock_response.json())


def mock_call_back(method, url):
    responses.add_callback(
        method, url, callback=callback,
        content_type='application/json'
    )


class TestZooServiceRequestHandler(unittest.TestCase):

    def setUp(self):
        self.handler = ZooServiceRequestHandler()

    def test_defaults(self):
        self.assertEqual(self.handler.timeout, 2)
        self.assertEqual(self.handler.request_attempts, 3)
        self.assertEqual(self.handler.monkey_addr, SERVER_URL + '/monkeys/')
        self.assertEqual(self.handler.zoo_addr, SERVER_URL + '/zoos/')

    @patch(REQUESTS_GET_PATCH)
    def test_handle_request_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')
        with self.assertRaises(NoResponse) as cm:
            self.handler.handle_request('http://oops')

        error = cm.exception
        expected = {
            'error': 504,
            'title': 'gateway timeout',
            'error_type': 'NoResponse',
            'text': 'at address: http://oops, attempts: 3, timeout after: 2 seconds'
        }
        self.assertEqual(json.loads(error.args[0]), expected)
        expected_calls = [call('http://oops', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @responses.activate
    def test_handle_request_no_timeout(self):
        responses.add(responses.GET, 'http://hi.com', body='hi')
        response = self.handler.handle_request('http://hi.com')
        self.assertEqual(response.content, b'hi')

    @responses.activate
    def test_get_all_monkeys(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/')

        response = self.handler.get_all_monkeys()
        expected = [
            {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1},
            {'id': 2, 'name': 'b', 'sex': 'f', 'flings_poop': 'TRUE', 'poop_size': 2, 'zoo_id': 1},
            {'id': 3, 'name': 'a', 'sex': 'm', 'flings_poop': 'FALSE', 'poop_size': 3, 'zoo_id': 2},
            {'id': 4, 'name': 'a', 'sex': 'f', 'flings_poop': 'FALSE', 'poop_size': 4, 'zoo_id': 2}
        ]
        self.assertEqual(response, expected)

    @responses.activate
    def test_get_all_zoos(self):
        mock_call_back(responses.GET, 'http://localhost:8080/zoos/')
        response = self.handler.get_all_zoos()
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
        self.assertEqual(response, expected)

    @responses.activate
    def test_get_zoo_correct_address(self):
        mock_call_back(responses.GET, 'http://localhost:8080/zoos/1')
        response = self.handler.get_zoo(1)
        expected = {
            'id': 1, 'name': 'a', 'opens': '12:00', 'closes': '13:00',
            'monkeys': [
                {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1},
                {'id': 2, 'name': 'b', 'sex': 'f', 'flings_poop': 'TRUE', 'poop_size': 2, 'zoo_id': 1}
            ]
        }
        self.assertEqual(response, expected)

    @responses.activate
    def test_get_zoo_incorrect_address(self):
        mock_call_back(responses.GET, 'http://localhost:8080/zoos/10')
        with self.assertRaises(BadResponse) as cm:
            self.handler.get_zoo(10)
        error = cm.exception
        error_json = json.loads(error.args[0])
        expected = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': error_json['text']
        }
        self.assertEqual(expected, error_json)

    @responses.activate
    def test_get_monkey_correct_address(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/1')
        response = self.handler.get_monkey(1)
        expected = {'id': 1, 'name': 'a', 'sex': 'm', 'flings_poop': 'TRUE', 'poop_size': 1, 'zoo_id': 1}
        self.assertEqual(response, expected)

    @responses.activate
    def test_get_monkey_incorrect_address(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/10')
        with self.assertRaises(BadResponse) as cm:
            self.handler.get_monkey(10)
        error = cm.exception
        error_json = json.loads(error.args[0])
        expected = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': error_json['text']
        }
        self.assertEqual(expected, error_json)

    @responses.activate
    def test_has_monkey_true(self):
        mock_call_back(responses.HEAD, 'http://localhost:8080/monkeys/1')
        self.assertTrue(self.handler.has_monkey(1))

    @responses.activate
    def test_has_monkey_false(self):
        mock_call_back(responses.HEAD, 'http://localhost:8080/monkeys/10')
        self.assertFalse(self.handler.has_monkey(10))

    @responses.activate
    def test_has_zoo_true(self):
        mock_call_back(responses.HEAD, 'http://localhost:8080/zoos/1')
        self.assertTrue(self.handler.has_zoo(1))

    @responses.activate
    def test_has_zoo_false(self):
        mock_call_back(responses.HEAD, 'http://localhost:8080/zoos/10')
        self.assertFalse(self.handler.has_zoo(10))

    @responses.activate
    def test_is_monkey_in_zoo_true(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/1')
        self.assertTrue(self.handler.is_monkey_in_zoo(1, 1))

    @responses.activate
    def test_is_monkey_in_zoo_false_by_wrong_zoo(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/1')
        self.assertFalse(self.handler.is_monkey_in_zoo(1, 2))

    @responses.activate
    def test_is_monkey_in_zoo_false_by_non_existent_zoo(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/1')
        self.assertFalse(self.handler.is_monkey_in_zoo(1, 200))

    @responses.activate
    def test_is_monkey_in_zoo_bad_monkey_id(self):
        mock_call_back(responses.GET, 'http://localhost:8080/monkeys/10')
        self.assertRaises(BadResponse, self.handler.is_monkey_in_zoo, 10, 1)

    @patch(REQUESTS_GET_PATCH)
    def test_get_all_zoos_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.get_all_zoos)

        expected_calls = [call('http://localhost:8080/zoos/', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_GET_PATCH)
    def test_get_all_monkeys_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.get_all_monkeys)

        expected_calls = [call('http://localhost:8080/monkeys/', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_GET_PATCH)
    def test_get_zoo_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.get_zoo, 1)

        expected_calls = [call('http://localhost:8080/zoos/1', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_GET_PATCH)
    def test_get_monkey_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.get_monkey, 1)

        expected_calls = [call('http://localhost:8080/monkeys/1', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_HEAD_PATCH)
    def test_has_monkey_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.has_monkey, 1)

        expected_calls = [call('http://localhost:8080/monkeys/1', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_HEAD_PATCH)
    def test_has_zoo_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.has_zoo, 1)

        expected_calls = [call('http://localhost:8080/zoos/1', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @patch(REQUESTS_GET_PATCH)
    def test_is_monkey_in_zoo_with_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout('nope')

        self.assertRaises(NoResponse, self.handler.is_monkey_in_zoo, 1, 1)

        expected_calls = [call('http://localhost:8080/monkeys/1', timeout=2)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)
