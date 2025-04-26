import os
import subprocess
import time

NODES_NUM = 10 # Represents the number of nodes. Should be no more than 10

for i in range(NODES_NUM + 1):
    if (i == NODES_NUM):
        PG_DATA_DIR = f"./coorddb"
        LOG_DB_NAME = "logcoord"
        PGPORT = str(8890)
    else:
        PG_DATA_DIR = f"./node{i}db"
        LOG_DB_NAME = f"lognode{i}"
        DATA_DB_NAME = f"datanode{i}"
        PGPORT = str(8880 + i)

    # Step 1: Create the directory if it doesn't exist
    if not os.path.exists(PG_DATA_DIR):
        os.makedirs(PG_DATA_DIR)
        print(f"Created directory: {PG_DATA_DIR}")
    else:
        print(f"Directory already exists: {PG_DATA_DIR}")

    time.sleep(0.1)

    # Step 2: Initialize the PostgreSQL data directory
    try:
        result = subprocess.run(
            ["initdb", "-D", PG_DATA_DIR],
            check=True,
            capture_output=False,
            text=False
        )
        print("initdb output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to initialize PostgreSQL data directory:")
        print(e.stderr)
        exit(1)
    
    time.sleep(1)

    # Step 3: Start the PostgreSQL cluster
    try:
        result = subprocess.run(
            [
                "pg_ctl", "start",
                "-D", PG_DATA_DIR,
                "-o", "-c max_prepared_transactions=99"
            ],
            check=True,
            capture_output=False,
            text=False,
            env={**os.environ, "PGPORT": PGPORT}
        )
        print("PostgreSQL cluster started successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to start PostgreSQL cluster:")
        print(e.stderr)
        exit(1)
    
    time.sleep(1)

    # Step 4: Create the log database
    try:
        result = subprocess.run(
            ["createdb", "-h", "localhost", "-p", PGPORT, LOG_DB_NAME],
            check=True,
            capture_output=False,
            text=False
        )
        print(f"Database '{LOG_DB_NAME}' created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create database '{LOG_DB_NAME}':")
        print(e.stderr)
        exit(1)

    # Step 5: Create the data database
    if (i != NODES_NUM):
        try:
            result = subprocess.run(
                ["createdb", "-h", "localhost", "-p", PGPORT, DATA_DB_NAME],
                check=True,
                capture_output=False,
                text=False
            )
            print(f"Database '{LOG_DB_NAME}' created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create database '{DATA_DB_NAME}':")
            print(e.stderr)
            exit(1)