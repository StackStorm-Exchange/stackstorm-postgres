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
from query import QueryAction
import mock


class TestActionQueryAction(PostgresBaseActionTestCase):
    __test__ = True
    action_cls = QueryAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, QueryAction)
        self.assertIsInstance(action, BaseAction)

    @mock.patch('query.QueryAction.postgres_query')
    @mock.patch('query.QueryAction.make_client')
    def test_run(self, mock_make_client, mock_query):
        action = self.get_action_instance({})

        # test variables
        test_select_columns = ['col1', 'col2']
        test_table = 'schema.table_name'
        test_trailing_clauses = 'ORDER BY time DESC'
        test_where_conditions = 'col2 > 100'
        expected_result = 'result'

        # mock
        mock_query.return_value = expected_result

        # run
        result = action.run(test_select_columns, test_table, test_trailing_clauses,
                            test_where_conditions, arg1='val1', arg2='val2')

        # assert
        self.assertEquals(result, expected_result)
        mock_query.assert_called_once_with(test_select_columns, test_table,
                                           test_where_conditions, test_trailing_clauses)
        mock_make_client.assert_called_once_with(arg1='val1', arg2='val2')
