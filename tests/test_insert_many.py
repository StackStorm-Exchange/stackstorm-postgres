#!/usr/bin/env python
# Copyright 2023 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from postgres_base_action_test_case import PostgresBaseActionTestCase
from lib.base_action import BaseAction
from insert_many import InsertManyAction
import mock


class TestActionInsertManyAction(PostgresBaseActionTestCase):
    __test__ = True
    action_cls = InsertManyAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, InsertManyAction)
        self.assertIsInstance(action, BaseAction)

    @mock.patch('insert_many.InsertManyAction.postgres_close')
    @mock.patch('insert_many.InsertManyAction.make_client')
    def test_run_no_table(self, mock_make_client, mock_close):
        action = self.get_action_instance({})

        # test variables
        test_data = [
            {'not_table': 'test', 'columns': {'col1': 'value1'}}
	]
        expected_result = 'result'

        # run
        with self.assertRaises(ValueError):
            action.run(test_data, arg1='val1', arg2='val2')

        # assert
        mock_make_client.assert_called_once_with(arg1='val1', arg2='val2')
        mock_close.assert_called_once()

    @mock.patch('insert_many.InsertManyAction.postgres_close')
    @mock.patch('insert_many.InsertManyAction.postgres_insert')
    @mock.patch('insert_many.InsertManyAction.make_client')
    def test_run_no_columns(self, mock_make_client, mock_insert, mock_close):
        action = self.get_action_instance({})

        # test variables
        test_data = [
            {'table': 'schema.table1', 'columns': {'col1': 'value1'}},
            {'table': 'schema.table1', 'no_columns': 'test'}
        ]
        expected_result = 'result'

        # mock
        mock_insert.return_value = expected_result

        # run
        with self.assertRaises(ValueError):
            action.run(test_data, arg1='val1', arg2='val2')

        # assert
        mock_make_client.assert_called_once_with(arg1='val1', arg2='val2')
        mock_insert.assert_called_once_with('schema.table1', {'col1': 'value1'})
        mock_close.assert_called_once()

    @mock.patch('insert_many.InsertManyAction.postgres_commit_close')
    @mock.patch('insert_many.InsertManyAction.postgres_insert')
    @mock.patch('insert_many.InsertManyAction.make_client')
    def test_run(self, mock_make_client, mock_insert, mock_close):
        action = self.get_action_instance({})

        # test variables
        test_data = [
            {'table': 'schema.table1', 'columns': {'col1': 'value1'}},
            {'table': 'schema.table1', 'columns': {'col1': 'value2'}},
            {'table': 'schema.table2', 'columns': {'col1': 'value1', 'col2': 'value0'}}
        ]
        expected_result = 'result'

        # mock
        mock_close.return_value = expected_result

        # run
        result = action.run(test_data, arg1='val1', arg2='val2')

        # assert
        self.assertEquals(result, expected_result)
        mock_make_client.assert_called_once_with(arg1='val1', arg2='val2')
        mock_close.assert_called_once()
        calls = [
            mock.call('schema.table1', {'col1': 'value1'}),
            mock.call('schema.table1', {'col1': 'value2'}),
            mock.call('schema.table2', {'col1': 'value1', 'col2': 'value0'})
        ]
        mock_insert.assert_has_calls(calls)
