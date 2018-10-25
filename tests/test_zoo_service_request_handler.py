import unittest
from unittest.mock import patch, call

import json

import requests

from zoo_keeper_server.zoo_service_request_handler import ZooServiceRequestHandler, NoResponse, BadResponse
from tests.mock_requests import MockRequests

REQUESTS_GET_PATCH = 'requests.get'
REQUESTS_HEAD_PATCH = 'requests.head'


class TestZooServiceRequestHandler(unittest.TestCase):

    def setUp(self):
        self.zoo_service_url = "http://localhost:8080"
        self.handler = ZooServiceRequestHandler(self.zoo_service_url)

    def test_defaults(self):
        self.assertEqual(self.handler.timeout, 2)
        self.assertEqual(self.handler.request_attempts, 3)
        self.assertEqual(self.handler.monkey_addr, self.zoo_service_url + '/monkeys/')
        self.assertEqual(self.handler.zoo_addr, self.zoo_service_url + '/zoos/')

    @patch(REQUESTS_GET_PATCH)
    def test_other_url(self, mock_get):
        handler = ZooServiceRequestHandler('new')
        handler.get_all_zoos()
        mock_get.assert_called_once_with('new/zoos/', timeout=2)

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

    def test_handle_request_no_connection(self):
        bad_port = '1000000000'
        bad_address = 'http://locahost:{}'.format(bad_port)

        with self.assertRaises(NoResponse) as cm:
            self.handler.handle_request(bad_address)
        error_json = json.loads(cm.exception.args[0])
        expected = {
            'error': 504,
            'title': 'gateway timeout',
            'error_type': 'NoResponse',
        }
        for key, value in expected.items():
            self.assertEqual(error_json[key], value)
        self.assertIn("HTTPConnectionPool(host=", error_json['text'])
        self.assertIn("port={}".format(bad_port), error_json['text'])

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_handle_request_no_timeout(self):
        response = self.handler.handle_request('http://localhost:8080/monkeys/1')
        expected = {'id': 1, 'zoo_id': 1}
        self.assertEqual(response.json(), expected)
        self.assertEqual(response.status_code, 200)

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_all_monkeys(self):

        response = self.handler.get_all_monkeys()
        expected = [
            {'id': 1, 'zoo_id': 1},
            {'id': 2, 'zoo_id': 1},
            {'id': 3, 'zoo_id': 2},
            {'id': 4, 'zoo_id': 2}
        ]
        self.assertEqual(response, expected)

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_all_zoos(self):
        response = self.handler.get_all_zoos()
        expected = [
            {'id': 1, 'monkeys': [{'id': 1, 'zoo_id': 1}, {'id': 2, 'zoo_id': 1}]},
            {'id': 2, 'monkeys': [{'id': 3, 'zoo_id': 2}, {'id': 4, 'zoo_id': 2}]}
        ]
        self.assertEqual(response, expected)

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_zoo_correct_address(self):
        response = self.handler.get_zoo(1)
        expected = {'id': 1, 'monkeys': [{'id': 1, 'zoo_id': 1}, {'id': 2, 'zoo_id': 1}]}
        self.assertEqual(response, expected)

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_zoo_incorrect_address(self):
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

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_monkey_correct_address(self):
        response = self.handler.get_monkey(1)
        expected = {'id': 1, 'zoo_id': 1}
        self.assertEqual(response, expected)

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_get_monkey_incorrect_address(self):
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

    @patch(REQUESTS_HEAD_PATCH, MockRequests.head)
    def test_has_monkey_true(self):
        self.assertTrue(self.handler.has_monkey(1))

    @patch(REQUESTS_HEAD_PATCH, MockRequests.head)
    def test_has_monkey_false(self):
        self.assertFalse(self.handler.has_monkey(10))

    @patch(REQUESTS_HEAD_PATCH, MockRequests.head)
    def test_has_zoo_true(self):
        self.assertTrue(self.handler.has_zoo(1))

    @patch(REQUESTS_HEAD_PATCH, MockRequests.head)
    def test_has_zoo_false(self):
        self.assertFalse(self.handler.has_zoo(10))

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_is_monkey_in_zoo_true(self):
        self.assertTrue(self.handler.is_monkey_in_zoo(1, 1))

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_is_monkey_in_zoo_false_by_wrong_zoo(self):
        self.assertFalse(self.handler.is_monkey_in_zoo(1, 2))

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_is_monkey_in_zoo_false_by_non_existent_zoo(self):
        self.assertFalse(self.handler.is_monkey_in_zoo(1, 200))

    @patch(REQUESTS_GET_PATCH, MockRequests.get)
    def test_is_monkey_in_zoo_bad_monkey_id(self):
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

    @patch(REQUESTS_GET_PATCH)
    def test_is_monkey_in_zoo_with_no_connection(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError('oops')
        with self.assertRaises(NoResponse) as cm:
            self.handler.is_monkey_in_zoo(1, 1)
        error_json = json.loads(cm.exception.args[0])

        expected = {
            'error': 504,
            'title': 'gateway timeout',
            'error_type': 'NoResponse',
            'text': 'oops'
        }
        self.assertEqual(expected, error_json)
