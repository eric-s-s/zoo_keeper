import unittest
from unittest.mock import patch

import requests

from tests.mock_requests import MockRequests

from zoo_keeper_server.zoo_service_request_handler import NoResponse
from zoo_keeper_server.validator import Validator

PATCH_REQUESTS_STRING = 'zoo_keeper_server.zoo_service_request_handler.requests'


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.validator = Validator()

    @patch(PATCH_REQUESTS_STRING, MockRequests)
    def test_is_zoo_ok(self):
        self.assertTrue(self.validator.is_zoo_ok(1))
        self.assertTrue(self.validator.is_zoo_ok(2))
        self.assertTrue(self.validator.is_zoo_ok(None))

        self.assertFalse(self.validator.is_zoo_ok(3))

    @patch(PATCH_REQUESTS_STRING, MockRequests)
    def test_is_favorite_monkey_ok(self):
        self.assertTrue(self.validator.is_favorite_monkey_ok(1, 1))
        self.assertTrue(self.validator.is_favorite_monkey_ok(2, 1))
        self.assertTrue(self.validator.is_favorite_monkey_ok(3, 2))
        self.assertTrue(self.validator.is_favorite_monkey_ok(4, 2))
        self.assertTrue(self.validator.is_favorite_monkey_ok(None, None))
        self.assertTrue(self.validator.is_favorite_monkey_ok(None, 10))

        self.assertFalse(self.validator.is_favorite_monkey_ok(1, 2))
        self.assertFalse(self.validator.is_favorite_monkey_ok(1, None))
        self.assertFalse(self.validator.is_favorite_monkey_ok(5, 1))
        self.assertFalse(self.validator.is_favorite_monkey_ok(1, 5))

    @patch(PATCH_REQUESTS_STRING, MockRequests)
    def test_is_dream_monkey_ok(self):
        self.assertTrue(self.validator.is_dream_monkey_ok(1, 2))
        self.assertTrue(self.validator.is_dream_monkey_ok(2, 2))
        self.assertTrue(self.validator.is_dream_monkey_ok(3, 1))
        self.assertTrue(self.validator.is_dream_monkey_ok(4, 1))
        self.assertTrue(self.validator.is_dream_monkey_ok(4, 10))
        self.assertTrue(self.validator.is_dream_monkey_ok(None, None))
        self.assertTrue(self.validator.is_dream_monkey_ok(None, 10))

        self.assertFalse(self.validator.is_dream_monkey_ok(1, 1))
        self.assertFalse(self.validator.is_dream_monkey_ok(1, None))
        self.assertFalse(self.validator.is_dream_monkey_ok(5, 1))

    @patch(PATCH_REQUESTS_STRING, MockRequests)
    def test_raise_value_errors_no_errors(self):
        kwargs_sets = [
            {'zoo_id': None, 'favorite_monkey_id': None, 'dream_monkey_id': None},
            {'zoo_id': 1, 'favorite_monkey_id': None, 'dream_monkey_id': None},
            {'zoo_id': 1, 'favorite_monkey_id': 1, 'dream_monkey_id': None},
            {'zoo_id': 1, 'favorite_monkey_id': None, 'dream_monkey_id': 3}
        ]
        for kwargs in kwargs_sets:
            self.assertIsNone(self.validator.raise_value_errors(**kwargs))

    @patch(PATCH_REQUESTS_STRING, MockRequests)
    def test_raise_value_errors_with_errors(self):
        kwargs_sets = [
            {'zoo_id': None, 'favorite_monkey_id': 1, 'dream_monkey_id': None},
            {'zoo_id': None, 'favorite_monkey_id': None, 'dream_monkey_id': 1},
            {'zoo_id': 1, 'favorite_monkey_id': 3, 'dream_monkey_id': None},
            {'zoo_id': 1, 'favorite_monkey_id': None, 'dream_monkey_id': 1},
            {'zoo_id': 1, 'favorite_monkey_id': 3, 'dream_monkey_id': 1}
        ]
        for kwargs in kwargs_sets:
            self.assertRaises(ValueError, self.validator.raise_value_errors, **kwargs)

    @patch("requests.head")
    @patch("requests.get")
    def test_raises_NoResponse_on_timeout(self, mock_get, mock_head):
        mock_get.side_effect = requests.exceptions.Timeout()
        mock_head.side_effect = requests.exceptions.Timeout()

        self.assertRaises(NoResponse, self.validator.is_zoo_ok, 100)
        self.assertRaises(NoResponse, self.validator.is_favorite_monkey_ok, 100, 100)
        self.assertRaises(NoResponse, self.validator.is_dream_monkey_ok, 100, 100)

        self.assertRaises(NoResponse, self.validator.raise_value_errors, 1, None, None)
        self.assertRaises(NoResponse, self.validator.raise_value_errors, 1, 1, None)
        self.assertRaises(NoResponse, self.validator.raise_value_errors, 1, None, 1)

    @patch("requests.head")
    @patch("requests.get")
    def test_returns_correctly_on_timeout(self, mock_get, mock_head):
        mock_get.side_effect = requests.exceptions.Timeout()
        mock_head.side_effect = requests.exceptions.Timeout()

        self.assertTrue(self.validator.is_zoo_ok(None))
        self.assertTrue(self.validator.is_favorite_monkey_ok(None, 100))
        self.assertTrue(self.validator.is_favorite_monkey_ok(None, None))
        self.assertTrue(self.validator.is_dream_monkey_ok(None, 100))
        self.assertTrue(self.validator.is_dream_monkey_ok(None, None))

        self.assertFalse(self.validator.is_dream_monkey_ok(100, None))
        self.assertFalse(self.validator.is_favorite_monkey_ok(100, None))

        kwargs_sets = [
            {'zoo_id': None, 'favorite_monkey_id': 1, 'dream_monkey_id': None},
            {'zoo_id': None, 'favorite_monkey_id': None, 'dream_monkey_id': 1},
            {'zoo_id': None, 'favorite_monkey_id': 1, 'dream_monkey_id': 1}
        ]
        for kwargs in kwargs_sets:
            self.assertRaises(ValueError, self.validator.raise_value_errors, **kwargs)
        self.assertIsNone(self.validator.raise_value_errors(None, None, None))
