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
#
# Python module docs
# https://www.psycopg.org/docs/module.html
from st2common.runners.base_action import Action
from psycopg2.extras import RealDictCursor
import psycopg2
import six

# options for login credentials in the config
CREDENTIALS_OPTIONS = [
    'credentials',
    'username',
    'password',
]


class BaseAction(Action):

    def resolve_credentials(self, **kwargs):
        """ Lookup credentials, by name, specified by the 'credentials' parameter
        during action invocation from the credentials dict stored in the config
        """
        # if there are no credentials specified in the config, we have nothing to lookup
        if not self.config.get('credentials'):
            return kwargs

        # get the name of credentials asked for during action invocation
        cred_name = kwargs.get('credentials')

        # if we couldn't find the 'credentials' from the parameters in the config
        # then try to use the default credential
        if not cred_name or cred_name not in self.config['credentials']:
            self.logger.debug('Credential [{}] is not in the config, trying [default]'
                              .format(cred_name))

            # if we couldn't find the default credential in the config (by name),
            # then raise an error
            cred_name = 'default'
            if cred_name not in self.config['credentials']:
                raise ValueError('Unable to find credentials [{}] or [default] in config'
                                 .format(kwargs.get('credentials')))

        # lookup the credential by name
        credentials = self.config['credentials'][cred_name]
        for k, v in six.iteritems(credentials):
            # skip if the user explicitly set this property during action invocation
            if kwargs.get(k) is not None:
                continue

            # only set the property if the value in the credential object is set
            if v is not None:
                kwargs[k] = v

        return kwargs

    def resolve_config(self, **kwargs):
        for k, v in six.iteritems(self.config):
            # skip if we're looking a `credentials` options
            if k in CREDENTIALS_OPTIONS:
                continue

            # skip if the user explicitly set this parameter when invoking the action
            if kwargs.get(k) is not None:
                continue

            # only set the property if the value is set in the config
            if v is not None:
                kwargs[k] = v

        return kwargs

    def make_client(self, **kwargs):
        kwargs = self.resolve_credentials(**kwargs)
        kwargs = self.resolve_config(**kwargs)

        self.postgres_client = psycopg2.connect(dbname=kwargs['db_name'],
                                                user=kwargs['username'],
                                                password=kwargs['password'],
                                                host=kwargs['server'],
                                                port=kwargs['port'])

        return self.postgres_client

    def postgres_close(self):
        if self.postgres_client:
            self.postgres_client.close()

        return

    def postgres_commit_close(self):
        if self.postgres_client:
            self.postgres_client.commit()
            self.postgres_client.close()

        return

    def postgres_query(self, columns, table, conditions, trailing_clauses):
        # Verify that a session has been created
        if not self.postgres_client:
            raise ValueError('ERROR: Must establish a Postgres session before querying data!')

        # columns should be a list of columns to return. If it is blank then select all
        if columns is None or len(columns) == 0:
            select_cols = '*'
        else:
            select_cols = ', '.join(columns)

        query_str = "SELECT {} FROM {}".format(select_cols, table)

        # Add where conditions if any were passed
        if conditions is not None and len(conditions) > 0:
            query_str += ' WHERE '
            query_str += ' AND '.join(conditions)

        if trailing_clauses is not None:
            query_str += ' '
            query_str += trailing_clauses

        query_str += ';'

        #print(query_str)

        cursor = self.postgres_client.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query_str)

        result = cursor.fetchall()

        return result

    # NOTE: This assumes that a postgres session was already created with make_client.
    #       It also does not automatically add the record to the database,
    #       the postgres_commit_close function should be called after this
    #       which will save updates and new data
    def postgres_insert(self, table, columns):
        # Verify that a session has been created
        if not self.postgres_client:
            raise ValueError('ERROR: Must establish a Postgres session before inserting data!')

        column_names = [str(key) for key in columns.keys()]
        column_values = [str(key) for key in columns.values()]

        query_str = "INSERT INTO {}({}) VALUES (".format(table, ', '.join(column_names))
        count = 0
        while count < len(column_values):
            append = '%s' if count + 1 == len(column_values) else '%s, '
            query_str += append
            count += 1
        query_str += ");"

        cursor = self.postgres_client.cursor()
        result = cursor.execute(query_str, column_values)

        return result

    def run(self, **kwargs):
        raise NotImplementedError()
