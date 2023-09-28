#!/usr/bin/env python
# Copyright 2023 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Python module docs
# https://www.psycopg.org/docs/module.html
from postgres_base_action_test_case import PostgresBaseActionTestCase
from lib.base_action import BaseAction
from st2common.runners.base_action import Action
from psycopg2.extras import RealDictCursor
import mock

class TestActionLibBaseAction(PostgresBaseActionTestCase):
    __test__ = True
    action_cls = BaseAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, BaseAction)
        self.assertIsInstance(action, Action)

    def test_resolve_credentials_no_config_credentials(self):
        action = self.get_action_instance({})
        action.config = {}
        result = action.resolve_credentials(test='kwargs')
        self.assertEquals(result, {'test': 'kwargs'})

    def test_resolve_credentials_default_credentials(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'default': {
                    'username': 'st2admin',
                    'password': 'secret',
                }
            }
        }
        result = action.resolve_credentials(test='kwargs')
        self.assertEquals(result, {'test': 'kwargs',
                                   'username': 'st2admin',
                                   'password': 'secret'})

    def test_resolve_credentials_non_exist_credentials_name(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'username': 'st2admin',
                    'password': 'secret',
                }
            }
        }
        with self.assertRaises(ValueError):
            action.resolve_credentials(credentials='doesnt_exist')

    def test_resolve_credentials_0no_kwargs_credentials_and_no_default_raises(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'username': 'st2admin',
                    'password': 'secret',
                }
            }
        }
        with self.assertRaises(ValueError):
            action.resolve_credentials(test='kwargs')

    def test_resolve_credentials_good_credentials(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'username': 'st2admin',
                    'password': 'secret',
                }
            }
        }
        result = action.resolve_credentials(credentials='qa', otherarg='othervalue')
        self.assertEquals(result, {
            'credentials': 'qa',
            'otherarg': 'othervalue',
            'username': 'st2admin',
            'password': 'secret',
        })

    def test_resolve_credentials_parameters_override_config(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'username': 'st2admin',
                    'password': 'secret',
                }
            }
        }
        result = action.resolve_credentials(credentials='qa',
                                            username='param_user')
        self.assertEquals(result, {
            'credentials': 'qa',
            'username': 'param_user',
            'password': 'secret',
        })

    def test_resolve_credentials_config_credentials_none_value(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'username': 'st2admin',
                    'password': None,
                }
            }
        }
        result = action.resolve_credentials(credentials='qa',
                                            username='param_user')
        self.assertEquals(result, {
            'credentials': 'qa',
            'username': 'param_user',
        })

    def test_resolve_config_no_kwargs(self):
        action = self.get_action_instance({})
        action.config = {'server': 'postgres.domain.tld',
                         'ssl': True}
        result = action.resolve_config()
        self.assertEquals(result, {'server': 'postgres.domain.tld',
                                   'ssl': True})

    def test_resolve_config_kwargs_override_config(self):
        action = self.get_action_instance({})
        action.config = {'ssl': True}
        result = action.resolve_config(ssl=False)
        self.assertEquals(result, {'ssl': False})

    def test_resolve_config_skip_credentials(self):
        action = self.get_action_instance({})
        action.config = {'username': 'st2admin',
                         'password': 'secret',
                         'credentials': 'default'}
        result = action.resolve_config()
        self.assertEquals(result, {})

    def test_resolve_config_none_values(self):
        action = self.get_action_instance({})
        action.config = {'server': None}
        result = action.resolve_config()
        self.assertEquals(result, {})

    @mock.patch('lib.base_action.BaseAction.resolve_config')
    @mock.patch('lib.base_action.BaseAction.resolve_credentials')
    @mock.patch('lib.base_action.psycopg2')
    def test_make_client(self, mock_psycopg, mock_creds, mock_config):
        action = self.get_action_instance({})

        test_kwargs = {'db_name': 'database',
                       'username': 'user',
                       'password': 'pass',
                       'server': 'postgres.domain.tld',
                       'port': 5432}
        expected_result = 'result'
        mock_psycopg.connect.return_value = expected_result
        mock_creds.return_value = test_kwargs
        mock_config.return_value = test_kwargs

        result = action.make_client(**test_kwargs)

        self.assertEquals(result, expected_result)
        mock_creds.assert_called_once_with(**test_kwargs)
        mock_config.assert_called_once_with(**test_kwargs)
        mock_psycopg.connect.assert_called_once_with(
            dbname='database',
            user='user',
            password='pass',
            host='postgres.domain.tld',
            port=5432)

    def test_postgres_close(self):
        action = self.get_action_instance({})

        mock_client = mock.MagicMock()
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client

        result = action.postgres_close()

        mock_client.close.assert_called_once()

    def test_postgres_close_no_client(self):
        action = self.get_action_instance({})

        mock_client = mock.MagicMock()
        mock_client.close.return_value = 'closed'
        action.postgres_client = None

        result = action.postgres_close()

        mock_client.close.assert_not_called()

    def test_postgres_commit_close(self):
        action = self.get_action_instance({})

        mock_client = mock.MagicMock()
        mock_client.commit.return_value = 'commit'
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client

        result = action.postgres_commit_close()

        mock_client.commit.assert_called_once()
        mock_client.close.assert_called_once()

    def test_postgres_commit_close_no_client(self):
        action = self.get_action_instance({})

        mock_client = mock.MagicMock()
        mock_client.commit.return_value = 'commit'
        mock_client.close.return_value = 'closed'
        action.postgres_client = None

        result = action.postgres_commit_close()

        mock_client.commit.assert_not_called()
        mock_client.close.assert_not_called()
    
    def test_postgres_insert_no_client(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = {'col1': 'value1'}
        action.postgres_client = None

        with self.assertRaises(ValueError):
            result = action.postgres_insert(test_table, test_columns)

    def test_postgres_insert(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = {'col1': 'value1', 'col2': 'value2'}
        expected_result = 'result'
        # The following query string was copied from postgres_insert.py
        test_query_str = 'INSERT INTO schema.table1(col1, col2) VALUES (%s, %s);'
        test_column_values = ['value1', 'value2']

        mock_cursor = mock.MagicMock()
        mock_cursor.execute.return_value = expected_result
        mock_client = mock.MagicMock()
        mock_client.cursor.return_value = mock_cursor
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client

        result = action.postgres_insert(test_table, test_columns)

        self.assertEquals(result, expected_result)
        mock_client.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(test_query_str, test_column_values)

    def test_postgres_query_no_client(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = ['col1', 'col2']
        test_conditions = []
        trailing_clauses = None
        action.postgres_client = None

        with self.assertRaises(ValueError):
            result = action.postgres_query(test_table, test_columns, test_conditions, trailing_clauses)

    def test_postgres_query(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = []
        test_conditions = []
        trailing_clauses = None
        expected_result = 'result'
        # The following query string was copied from postgres_insert.py
        test_query_str = 'SELECT * FROM schema.table1;'

        mock_cursor = mock.MagicMock()
        mock_cursor.execute.return_value = ['results']
        mock_cursor.fetchall.return_value = expected_result
        mock_client = mock.MagicMock()
        mock_client.cursor.return_value = mock_cursor
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client
        result = action.postgres_query(test_columns, test_table, test_conditions, trailing_clauses)

        self.assertEquals(result, expected_result)
        mock_client.cursor.assert_called_once_with(cursor_factory=RealDictCursor)
        mock_cursor.execute.assert_called_once_with(test_query_str)

    def test_postgres_query_condition_clause(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = ['col1', 'col2']
        test_conditions = ['time > NOW() - INTERVAL \'15 minutes\'']
        trailing_clauses = 'ORDER BY col2 DESC'
        expected_result = 'result'
        # The following query string was copied from postgres_insert.py
        test_query_str = 'SELECT col1, col2 FROM schema.table1 WHERE time > NOW() - INTERVAL ' \
            '\'15 minutes\' ORDER BY col2 DESC;'

        mock_cursor = mock.MagicMock()
        mock_cursor.execute.return_value = ['results']
        mock_cursor.fetchall.return_value = expected_result
        mock_client = mock.MagicMock()
        mock_client.cursor.return_value = mock_cursor
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client

        result = action.postgres_query(test_columns, test_table, test_conditions, trailing_clauses)

        self.assertEquals(result, expected_result)
        mock_client.cursor.assert_called_once_with(cursor_factory=RealDictCursor)
        mock_cursor.execute.assert_called_once_with(test_query_str)

    def test_postgres_query_conditions(self):
        action = self.get_action_instance({})

        test_table = 'schema.table1'
        test_columns = ['col1', 'col2']
        test_conditions = ['col1 > 100', 'time > NOW() - INTERVAL \'15 minutes\'']
        trailing_clauses = None
        expected_result = 'result'
        # The following query string was copied from postgres_insert.py
        test_query_str = 'SELECT col1, col2 FROM schema.table1 WHERE col1 > 100 AND time ' \
            '> NOW() - INTERVAL \'15 minutes\';'

        mock_cursor = mock.MagicMock()
        mock_cursor.execute.return_value = ['results']
        mock_cursor.fetchall.return_value = expected_result
        mock_client = mock.MagicMock()
        mock_client.cursor.return_value = mock_cursor
        mock_client.close.return_value = 'closed'

        action.postgres_client = mock_client

        result = action.postgres_query(test_columns, test_table, test_conditions, trailing_clauses)

        self.assertEquals(result, expected_result)
        mock_client.cursor.assert_called_once_with(cursor_factory=RealDictCursor)
        mock_cursor.execute.assert_called_once_with(test_query_str)

    def test_run(self):
        action = self.get_action_instance({})
        with self.assertRaises(NotImplementedError):
            action.run()
