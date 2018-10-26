import unittest
from unittest.mock import patch

import json

from zoo_keeper_server import flask_app
from zoo_keeper_server.db_request_handler import DBRequestHandler, BadData, BadId
from tests.create_test_data import TestSession, create_simple_test_data
from tests.mock_requests import MockRequests

HANDLER_PATCH_STR = 'zoo_keeper_server.flask_app.DBRequestHandler'
SESSION_PATCH_STR = 'zoo_keeper_server.data_base_session.DataBaseSession'


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.app.test_client()
        self.session = TestSession()
        flask_app.app.testing = True
        create_simple_test_data(self.session)
        TestSession.reset_close_count()

    @patch('requests.get', MockRequests.get)
    @patch(SESSION_PATCH_STR, TestSession)
    def test_all_zoo_keepers_get(self):
        response = self.app.get('/zoo_keepers/')

        expected = [
            {'id': 1, 'name': 'a', 'age': 1, 'zoo_id': 1, 'favorite_monkey_id': 2, 'dream_monkey_id': 1,
             'dream_monkey': {'id': 1, 'zoo_id': 1},
             'favorite_monkey': {'id': 2, 'zoo_id': 1},
             'zoo': {'id': 1, 'monkeys': [{'id': 1, 'zoo_id': 1}, {'id': 2, 'zoo_id': 1}]},
             },
            {'id': 2, 'name': 'b', 'age': 2, 'zoo_id': None, 'favorite_monkey_id': None, 'dream_monkey_id': None,
             'zoo': {}, 'favorite_monkey': {}, 'dream_monkey': {}},
        ]
        self.assertEqual(json.loads(response.data), expected)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestSession.close_counts(), 1)

    @patch(SESSION_PATCH_STR, TestSession)
    @patch("requests.get", MockRequests.get)
    def test_all_zoo_keepers_post(self):

        json_data = {'name': 'q', 'age': 5}
        response = self.app.post('/zoo_keepers/', json=json_data)
        expected = {
            'id': 3, 'name': 'q', 'age': 5, 'zoo_id': None, 'favorite_monkey_id': None, 'dream_monkey_id': None,
            'zoo': {}, 'favorite_monkey': {}, 'dream_monkey': {}
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected)

        self.assertEqual(TestSession.close_counts(), 1)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoo_keepers_post_bad_data(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        bad_data = 'hi'
        handler_instance.post_zoo_keeper.side_effect = BadData(bad_data)

        response = self.app.post('/zoo_keepers/', json={})

        response_json = json.loads(response.data)
        expected = {
            'error': 400,
            'error_type': 'BadData',
            'title': 'bad request',
            'text': bad_data
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 400)
        handler_instance.post_zoo_keeper.assert_called_once_with(session_instance, {})
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoo_keepers_post_bad_json_str(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)

        response = self.app.post('/zoo_keepers/', content_type="application/json", data='{"so bad":')

        response_json = json.loads(response.data)
        expected = {
            'error': 400,
            'error_type': 'BadRequest',
            'title': 'bad request',
            'text': response_json['text']
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 400)
        handler_instance.post_zoo_keeper.assert_not_called()
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoo_keepers_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_zoo_keepers.return_value = 'good', 200

        response = self.app.head('/zoo_keepers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"")

        handler_instance.get_all_zoo_keepers.assert_called_once_with(session_instance)
        session_instance.close.assert_called_once_with()

    @patch("requests.get", MockRequests.get)
    def test_all_monkeys_get(self):
        response = self.app.get('/monkeys/')
        expected =[
            {'id': 1, 'zoo_id': 1},
            {'id': 2, 'zoo_id': 1},
            {'id': 3, 'zoo_id': 2},
            {'id': 4, 'zoo_id': 2}
        ]
        self.assertEqual(json.loads(response.data), expected)
        self.assertEqual(response.status_code, 200)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_monkeys_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_monkeys.return_value = 'good', 200

        response = self.app.head('/monkeys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"")

        handler_instance.get_all_monkeys.assert_called_once_with()

    @patch("requests.get", MockRequests.get)
    def test_all_zoos_get(self):
        response = self.app.get('/zoos/')
        expected =[
            {'id': 1, 'monkeys': [{'id': 1, 'zoo_id': 1}, {'id': 2, 'zoo_id': 1}]},
            {'id': 2, 'monkeys': [{'id': 3, 'zoo_id': 2}, {'id': 4, 'zoo_id': 2}]}
        ]
        self.assertEqual(json.loads(response.data), expected)
        self.assertEqual(response.status_code, 200)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoos_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_zoos.return_value = 'ok', 200

        response = self.app.head('/zoos/')

        self.assertEqual(response.data, b"")
        self.assertEqual(response.status_code, 200)
        handler_instance.get_all_zoos.assert_called_once_with()

    @patch(SESSION_PATCH_STR, TestSession)
    @patch("requests.get", MockRequests.get)
    def test_zoo_keeper_by_id_get(self):

        response = self.app.get('/zoo_keepers/2')
        expected = {'id': 2, 'name': 'b', 'age': 2, 'zoo_id': None, 'zoo': {},
                    'favorite_monkey_id': None, 'favorite_monkey': {},
                    'dream_monkey_id': None, 'dream_monkey': {}}
        self.assertEqual(json.loads(response.data), expected)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(TestSession.close_counts(), 1)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_get_error(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_zoo_keeper.side_effect = BadId('no')

        response = self.app.get('/zoo_keepers/100')
        response_json = json.loads(response.data)
        expected = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': "no"
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 404)
        handler_instance.get_zoo_keeper.assert_called_once_with(session_instance, '100')
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR, TestSession)
    @patch("requests.get", MockRequests.get)
    def test_zoo_keeper_by_id_delete(self):
        response = self.app.delete('/zoo_keepers/1')
        all_keepers = [
            {'age': 2, 'dream_monkey': {}, 'dream_monkey_id': None, 'favorite_monkey': {},
             'favorite_monkey_id': None, 'id': 2, 'name': 'b', 'zoo': {}, 'zoo_id': None}
        ]
        self.assertEqual(json.loads(response.data), all_keepers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TestSession.close_counts(), 1)

        bad_id = self.app.get('/zoo_keepers/1')
        error_msg = {'error': 404, 'error_type': 'BadId', 'text': 'id does not exist: 1', 'title': 'not found'}
        self.assertEqual(json.loads(bad_id.data), error_msg)
        self.assertEqual(bad_id.status_code, 404)
        self.assertEqual(TestSession.close_counts(), 2)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_delete_bad_id(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.delete_zoo_keeper.side_effect = BadId("nope")

        response = self.app.delete('/zoo_keepers/1000')
        response_json = json.loads(response.data)
        expected = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': "nope"
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 404)
        handler_instance.delete_zoo_keeper.assert_called_once_with(session_instance, '1000')
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR, TestSession)
    @patch("requests.get", MockRequests.get)
    def test_zoo_keeper_by_id_put(self):

        response = self.app.put('/zoo_keepers/2', json={'age': 100})
        expected = {
            'id': 2, 'name': 'b', 'age': 100, 'zoo_id': None, 'favorite_monkey_id': None,
            'dream_monkey_id': None, 'zoo': {}, 'dream_monkey': {}, 'favorite_monkey': {}
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected)
        self.assertEqual(TestSession.close_counts(), 1)

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_put_bad_id(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.put_zoo_keeper.side_effect = BadId('nope')

        response = self.app.put('/zoo_keepers/1', json={'a': 1})
        response_json = json.loads(response.data)
        expected = {
            'error': 404,
            'error_type': 'BadId',
            'title': 'not found',
            'text': "nope"
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 404)
        handler_instance.put_zoo_keeper.assert_called_once_with(session_instance, '1', {'a': 1})
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_put_bad_data(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.put_zoo_keeper.side_effect = BadData('nope')

        response = self.app.put('/zoo_keepers/1', json={'a': 1})
        response_json = json.loads(response.data)
        expected = {
            'error': 400,
            'error_type': 'BadData',
            'title': 'bad request',
            'text': "nope"
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 400)
        handler_instance.put_zoo_keeper.assert_called_once_with(session_instance, '1', {'a': 1})
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_bad_json(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)

        response = self.app.put('/zoo_keepers/1', content_type='application/json', data="{damnit: 1")
        response_json = json.loads(response.data)
        expected = {
            'error': 400,
            'error_type': 'BadRequest',
            'title': 'bad request',
            'text': response_json['text']
        }
        self.assertEqual(response_json, expected)
        self.assertEqual(response.status_code, 400)
        handler_instance.put_zoo_keeper.assert_not_called()
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_zoo_keeper.return_value = 'ok', 200

        response = self.app.head('/zoo_keepers/1')

        self.assertEqual(response.data, b"")
        self.assertEqual(response.status_code, 200)
        handler_instance.get_zoo_keeper.assert_called_once_with(session_instance, '1')
        session_instance.close.assert_called_once_with()


def create_instances(handler_class_mock, session_class_mock):
    handler_instance = handler_class_mock.return_value
    session_instance = session_class_mock.return_value
    handler_instance.mock_add_spec(DBRequestHandler)
    return handler_instance, session_instance
