# Two-phase Commit Server Implementation

This is a simple implementation of a
[two-phase commit protocol](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
in Python. Agents communicate through a RPC-like protocol that uses JSON for
serialization. Participant nodes write to a backing PostgreSQL database for
both logs and data. Using logs and the two-phase commit protocol, atomicity
and consistency of writes to the database is ensured in a network of
non-byzantine, but possibly failing nodes.

This program is the result of a project in the CS 223 Transaction Processing
and Distributed Data Management course by at the University of California,
Irvine.

## Installation

### Set up databases

PostgreSQL must be installed on the system for the databases.
We need `N` independent PostgreSQL server instances to act as
seperate nodes. Hence, create seperate databases (with their
own data directories) using

    initdb -D /path/to/data/directory

Then start the servers using

    pg_ctl start -D /path/to/data/directory

The port to run the server on can be given in `postgresql.conf` in
the data directory or using the `PGPORT` environment variable:

    env PGPORT=1234 pg_ctl start -D /path/to/data/directory

### Set up Python environment

Run with Python 3. Required package:

- `psycopg2`: Python Interface to PostgreSQL

  To install in a virtual environment on macOS, the library path
  for lib SSL might be explicitly provided as such:

      env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip --no-cache install psycopg2

## Running the nodes

For all of the following, you may set up databases ahead of time, or
let the script start them. If no database info is given as command line
arguments, a new database cluster in a temporary directory will be
automatically created.

For all of the nodes, that nodes own host name and port is given using
the `--host` argument. For coordinator node, the participant nodes
can be listed using multiple `--participant` arguments. For the participant
nodes, the coordinator node is given using the `--coordinator` argument.
Participant nodes must be consecutively numbered, starting from zero, using
the `--node-id` argument. The coordinator node takes optional
`--timeout` and `--batch-size` arguments.

Start the coordinator:

    python main.py
      --host localhost:9990
      --participant localhost:9991 --participant localhost:9992
      --log-db {dbname}
      --log-db-host {dbhost}

Start the participants

    python main.py
      --node-id 0
      --host localhost:9991
      --coordinator localhost:9990
      --log-db {logdbname}
      --log-db-host {logdbhost}
      --data-db {datadbname}
      --data-db-host {datadbhost}

    python main.py --node-id 1 --host localhost:9992 --coordinator localhost:9991
    ...

Start a client to interactively send insert requests to the coordinator:

    python client.py --coordinator localhost:9990

Start a client in demo mode which completes operations automatically:

    python client.py --coordinator localhost:9990 --demo thermometerobservations --n-nodes {number of participant nodes}

There is a script provided to automatically initialize and start nodes and their corresponding databases. This script is in setup.py file. Simply run it with

    python setup.py

After the program has finished simulations, all the logs of all the nodes including coordinator and client's log will be available at automatically generated /logs folder. Lastly, don't forget to terminate all processes and remove databases by executing:

    python3 setup.py close-clean

It will automatically delete all initialized databases and nodes instances.
