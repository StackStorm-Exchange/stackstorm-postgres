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
from lib.base_action import BaseAction


class InsertManyAction(BaseAction):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(InsertManyAction, self).__init__(config)

    def run(self, data, **kwargs):
        self.make_client(**kwargs)

        for record in data:
            # If any data is missing either a table or columns then close the connection without
            # committing anything
            if 'columns' not in record:
                self.postgres_close()
                raise ValueError("No columns given to add to table: ".format(record['table']))
            elif 'table' not in record:
                self.postgres_close()
                raise ValueError("No table given to add data: ".format(record['columns']))

            print("Adding {} to table: {}".format(record['columns'], record['table']))
            self.postgres_insert(record['table'], record['columns'])

        result = self.postgres_commit_close()

        return result
