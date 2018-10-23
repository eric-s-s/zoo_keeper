import unittest
from unittest.mock import patch

import json

from zoo_keeper_server import flask_app
from zoo_keeper_server.db_request_handler import DBRequestHandler, BadData, BadId


HANDLER_PATCH_STR = 'zoo_keeper_server.flask_app.DBRequestHandler'
SESSION_PATCH_STR = 'zoo_keeper_server.data_base_session.DataBaseSession'


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = flask_app.app.test_client()
        flask_app.app.testing = True

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoo_keepers_get(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_zoo_keepers.return_value = 'ok', 200

        response = self.app.get('/zoo_keepers/')
        self.assertEqual(response.data, b'ok')
        self.assertEqual(response.status_code, 200)

        handler_instance.get_all_zoo_keepers.assert_called_once_with(session_instance)
        session_instance.close.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoo_keepers_post(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.post_zoo_keeper.return_value = 'ok', 200

        json_data = {'a': 1}
        response = self.app.post('/zoo_keepers/', json=json_data)
        self.assertEqual(response.data, b'ok')
        self.assertEqual(response.status_code, 200)

        handler_instance.post_zoo_keeper.assert_called_once_with(session_instance, json_data)
        session_instance.close.assert_called_once_with()

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

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_monkeys_get(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_monkeys.return_value = 'ok', 200

        response = self.app.get('/monkeys/')
        self.assertEqual(response.data, b'ok')
        self.assertEqual(response.status_code, 200)

        handler_instance.get_all_monkeys.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_monkeys_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_monkeys.return_value = 'good', 200

        response = self.app.head('/monkeys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"")

        handler_instance.get_all_monkeys.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoos_get(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_zoos.return_value = 'good', 200

        response = self.app.get('/zoos/')
        self.assertEqual(response.data, b'good')
        self.assertEqual(response.status_code, 200)

        handler_instance.get_all_zoos.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_all_zoos_head(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_all_zoos.return_value = 'ok', 200

        response = self.app.head('/zoos/')

        self.assertEqual(response.data, b"")
        self.assertEqual(response.status_code, 200)
        handler_instance.get_all_zoos.assert_called_once_with()

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_get(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.get_zoo_keeper.return_value = 'ok', 200

        response = self.app.get('/zoo_keepers/1')
        self.assertEqual(response.data, b'ok')
        self.assertEqual(response.status_code, 200)
        handler_instance.get_zoo_keeper.assert_called_once_with(session_instance, '1')
        session_instance.close.assert_called_once_with()

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

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_delete(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.delete_zoo_keeper.return_value = 'ok', 200
        response = self.app.delete('/zoo_keepers/1')
        self.assertEqual(response.data, b'ok')
        self.assertEqual(response.status_code, 200)
        handler_instance.delete_zoo_keeper.assert_called_once_with(session_instance, '1')
        session_instance.close.assert_called_once_with()

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

    @patch(SESSION_PATCH_STR)
    @patch(HANDLER_PATCH_STR)
    def test_zoo_keeper_by_id_put(self, handler_class, session_class):
        handler_instance, session_instance = create_instances(handler_class, session_class)
        handler_instance.put_zoo_keeper.return_value = 'ok', 200

        response = self.app.put('/zoo_keepers/1', json={'a': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'ok')
        handler_instance.put_zoo_keeper.assert_called_once_with(session_instance, '1', {'a': 1})
        session_instance.close.assert_called_once_with()

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
