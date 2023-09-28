# Postgres Integration Pack

This pack interfaces with the [PostgreSQL](https://www.postgresql.org/) Python module [psycopg2](https://pypi.org/project/psycopg2/).
Actions are available to both query for and insert data to a PostgreSQL Database.
This pack utilizes PostgreSQL terminology, for more information we suggest reviewing
the [getting started](https://www.postgresqltutorial.com/postgresql-getting-started/) section,
the [cheat sheet](https://www.postgresqltutorial.com/postgresql-cheat-sheet/), and
[additional resources](https://www.postgresqltutorial.com/postgresql-resources/).

## Configuration

Copy the example configuration in [postgres.yaml.example](./postgres.yaml.example)
to `/opt/stackstorm/configs/postgres.yaml` and edit as required.

* `server` - The hostname/IP of the default Postgres server.
* `port` - Port number to connect to Postgres on (default: 5432)
* `db_name` - Name of database to connect to
* `credentials` - Mapping of name to an object containing credential information
  * `username` - User to authenticate as
  * `password` - Password to authenticate with.

**Note** : All actions allow you to specify a `credentials` parameter that will
           reference the `credentials` information in the config. Alternatively
           all actions allow you to override these credential parameters so a
           config isn't required.

**Note** : When modifying the configuration in `/opt/stackstorm/configs/` please
           remember to tell StackStorm to load these new values by running
           `st2ctl reload --register-configs`

### Configuration Credentials

Most options in the config are simply key/value pairs, with the exception of `credentials`.
In order to make working with the Postgres pack easier, we've provided a mechanism to
store credentials in the pack's config. Credentials are stored as a dictionary, sometimes
called a hash, where the key is the name of the credential and the values are 
the credential information (username, password, etc).

Below is an example of a simple config with a single credential named `dev`:

``` yaml
credentials:
  dev:
    username: 'test_user'
    password: 'myPassword'
```

Multiple credentials can also be specified:

``` yaml
credentials:
  dev:
    username: 'test_user'
    password: 'myPassword'
  qa:
    username: 'qa_user'
    password: 'xxxYYYzzz!!!'
  prod:
    username: 'prod_user'
    password: 'lkdjfldsfjO#U)R$'
```

These credentials can then be referenced by name when executing a `postgres` pack action
using the `credentials` parameter available on every action. Example:

``` shell
# use login information from the "dev" credential stored in the config
st2 run POSTGRES.QUERY 
```

### Configuration Credentials - Default

If a credential parameter is not specified, then we will attempt to lookup a credential
with the name of `default`. This allows end users to specify a default set of credentials
to be used via the config.

Example config:
``` yaml
credentials:
  default:
    username: 'default_user'
    password: 'abc123'
```

Example command using default credentials

``` shell
# use login information from the "default" credential stored in the config because
# the credentials parameter was not pass in
st2 run postgres.query table="breakers.branch_current_phase_1" server="postgres.domain.tld"
```

### Configuration Example

The configuration below is an example of what a end-user config might look like.
One of the most common config options will most likely be the `modulepath`, that will
direct `bolt` at the place where they've installed their Puppet modules.

``` yaml
---
server: postgres.domain.tld
port: 5432
db_name: mydatabase

credentials:
  default:
    username: 'myuser'
    password: 'secretSauce!'
```


# Actions

* `query` - Query data with SELECT FROM WHERE syntax. [/query](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-select/)
* `insert` - Insert a Postgres record into the given table with the given columns. [/insert](https://www.postgresql.org/docs/current/sql-insert.html)
* `insert_many` - Insert many Postgres records into one or more tables. [/insert_many](https://www.postgresql.org/docs/current/sql-insert.html)


## Action Example - query

Query data with SELECT FROM WHERE syntax [PostgreSQL](https://www.postgresqltutorial.com/postgresql-tutorial/postgresql-select/)
syntax.

``` shell
$ st2 run postgres.query table="breakers.branch_current_phase_1" where_conditions="time > NOW() - INTERVAL '15 minutes'" trailing_clauses="ORDER BY time DESC LIMIT 1"
.
id: 6515db05b96eb0d929f33680
action.ref: postgres.query
context.user: svc_stackstorm_puppet@mgt.encore.tech
parameters: 
  table: breakers.branch_current_phase_1
  trailing_clauses: ORDER BY time DESC LIMIT 1
  where_conditions:
  - time > NOW() - INTERVAL '15 minutes'
status: succeeded
start_timestamp: Thu, 28 Sep 2023 19:59:01 UTC
end_timestamp: Thu, 28 Sep 2023 19:59:02 UTC
result: 
  exit_code: 0
  result:
  - breaker: CUST-breaker
    customer: CUST
    panel: 1
    pdu_rdc: PDU-N1-A1
    time: '2023-09-28T15:50:28.987548-04:00'
    value: 1.5
    whip_pair: 129.14-4
  stderr: ''
  stdout: ''

```

## Action Example - insert

Insert a Postgres record into the given table with the given columns. https://www.postgresql.org/docs/current/sql-insert.html

``` shell
$ st2 run postgres.insert table="breakers.branch_current_phase_1" columns='{"time": "NOW()", "breaker": "breaker-name", "customer": "CUST", "panel": 1, "pdu_rdc": "PDU-N1-A1", "value": "1.5"}'
.
id: 6515da4db96eb0d929f3367d
action.ref: postgres.insert
context.user: svc_stackstorm_puppet@mgt.encore.tech
parameters: 
  columns:
    breaker: breaker-name
    customer: CUST
    panel: 1
    pdu_rdc: PDU-N1-A1
    time: NOW()
    value: '1.5'
  table: breakers.branch_current_phase_1
status: succeeded
start_timestamp: Thu, 28 Sep 2023 19:55:57 UTC
end_timestamp: Thu, 28 Sep 2023 19:55:58 UTC
result: 
  exit_code: 0
  result: null
  stderr: ''
  stdout: ''

```

## Action Example - insert many

Insert many Postgres records into one or more tables. https://www.postgresql.org/docs/current/sql-insert.html

```shell
$ st2 run postgres.insert_many data='[{"table": "breakers.branch_current_phase_1", "columns": {"time": "NOW()", "breaker": "breaker-name", "customer": "FLM", "panel": 1, "pdu_rdc": "PDU-N1-A1", "value": "1.5"}}]'
.
id: 6515dedeb96eb0d929f3368c
action.ref: postgres.insert_many
context.user: svc_stackstorm_puppet@mgt.encore.tech
parameters: 
  data:
  - columns:
      breaker: breaker-name
      customer: CUST
      panel: 1
      pdu_rdc: PDU-N1-A1
      time: NOW()
      value: '1.5'
    table: breakers.branch_current_phase_1
status: succeeded
start_timestamp: Thu, 28 Sep 2023 20:15:26 UTC
end_timestamp: Thu, 28 Sep 2023 20:15:26 UTC
result: 
  exit_code: 0
  result: null
  stderr: ''
  stdout: 'Adding {''time'': ''NOW()'', ''breaker'': ''breaker-name'', ''customer'': ''CUST'', ''panel'': 1, ''pdu_rdc'': ''PDU-N1-A1'', ''value'': ''1.5''} to table: breakers.branch_current_phase_1
    '

```
