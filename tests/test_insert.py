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
from insert import InsertAction
import mock


class TestActionInsertAction(PostgresBaseActionTestCase):
    __test__ = True
    action_cls = InsertAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, InsertAction)
        self.assertIsInstance(action, BaseAction)

    @mock.patch('insert.InsertAction.postgres_commit_close')
    @mock.patch('insert.InsertAction.postgres_insert')
    @mock.patch('insert.InsertAction.make_client')
    def test_run(self, mock_make_client, mock_insert, mock_close):
        action = self.get_action_instance({})

        # test variables
        test_columns = {'col1': 'value1'}
        test_table = 'schema.table_name'
        expected_result = 'result'

        # mock
        mock_insert.return_value = expected_result

        # run
        result = action.run(test_columns, test_table, arg1='val1', arg2='val2')

        # assert
        self.assertEquals(result, expected_result)
        mock_insert.assert_called_once_with(test_table, test_columns)
        mock_make_client.assert_called_once_with(arg1='val1', arg2='val2')
        mock_close.assert_called_once()
