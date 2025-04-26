import os
import subprocess
import time
import logging
import sys

NODES_NUM = 10  # Represents the number of nodes. Should be no more than 10
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SETUP_DIR, "logs")
# Create a file to store PIDs
pids_file = os.path.join(SETUP_DIR, "node_pids.txt")
bash_script_path = os.path.join(SETUP_DIR, "start_nodes.sh")


def startup():
    """
    Initialize PostgreSQL databases, create commands for nodes,
    and generate a bash script to run all nodes with logging.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created logs directory: {LOG_DIR}")

    # Setup PostgreSQL databases
    for i in range(NODES_NUM + 1):
        if i == NODES_NUM:
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
                text=False,
            )
            print("initdb output:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Failed to initialize PostgreSQL data directory:")
            print(e.stderr)
            exit(1)

        time.sleep(3)

        # Step 3: Start the PostgreSQL cluster
        try:
            result = subprocess.run(
                [
                    "pg_ctl",
                    "start",
                    "-D",
                    PG_DATA_DIR,
                    "-o",
                    "-c max_prepared_transactions=99",
                ],
                check=True,
                capture_output=False,
                text=False,
                env={**os.environ, "PGPORT": PGPORT},
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
                text=False,
            )
            print(f"Database '{LOG_DB_NAME}' created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create database '{LOG_DB_NAME}':")
            print(e.stderr)
            exit(1)

        # Step 5: Create the data database
        if i != NODES_NUM:
            try:
                result = subprocess.run(
                    ["createdb", "-h", "localhost", "-p", PGPORT, DATA_DB_NAME],
                    check=True,
                    capture_output=False,
                    text=False,
                )
                print(f"Database '{LOG_DB_NAME}' created successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Failed to create database '{DATA_DB_NAME}':")
                print(e.stderr)
                exit(1)

    # Setup commands for nodes with logging configuration
    exec_cmds = []

    coordinator = "localhost:9010"
    coordinator_db = "localhost:8890"
    participants = []
    participants_db = []
    for i in range(NODES_NUM):
        participants.append(f"localhost:900{i}")
        participants_db.append(f"localhost:888{i}")

    script_path = os.path.join(SETUP_DIR, "main.py")

    # Coordinator command with logging
    coordinator_log_file = os.path.join(LOG_DIR, "coordinator.log")
    coordinator_setup_command = f"python3 {script_path} --host {coordinator}"
    for participant in participants:
        coordinator_setup_command += f" --participant {participant}"
    coordinator_setup_command += " --log-db logcoord"
    coordinator_setup_command += f" --log-db-host {coordinator_db}"
    coordinator_setup_command += f" --batch-size {len(participants)}"
    coordinator_setup_command += f" > {coordinator_log_file} 2>&1"

    exec_cmds.append(coordinator_setup_command)

    # Participant commands with logging
    for i, participant in enumerate(participants):
        participant_log_file = os.path.join(LOG_DIR, f"participant_{i}.log")
        participant_setup_command = f"python3 {script_path} --node-id {i} --host {participant} --coordinator {coordinator} --log-db lognode{i} --log-db-host {participants_db[i]} --data-db datanode{i} --data-db-host {participants_db[i]}"
        participant_setup_command += f" > {participant_log_file} 2>&1"
        exec_cmds.append(participant_setup_command)

    # Client command with logging
    client_path = os.path.join(SETUP_DIR, "client.py")
    client_log_file = os.path.join(LOG_DIR, "client.log")
    client_command = f"python3 {client_path} --coordinator {coordinator} --demo thermometerobservation --n-nodes {NODES_NUM} > {client_log_file} 2>&1"
    exec_cmds.append(client_command)

    # Create a bash script to run all nodes and save PIDs
    with open(bash_script_path, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Generated script to start all nodes\n")
        f.write("echo 'Starting all nodes...'\n\n")

        # Clear previous PIDs file
        f.write(f"echo -n '' > {pids_file}\n\n")

        # Start coordinator
        f.write(f"# Start coordinator\n")
        f.write(f"echo 'Starting coordinator...'\n")
        f.write(f"nohup {exec_cmds[0]} & \n")
        f.write(f"COORD_PID=$!\n")
        f.write(f'echo "coordinator:$COORD_PID" >> {pids_file}\n')
        f.write("sleep 2\n\n")  # Give coordinator time to start

        # Start participants
        for i in range(NODES_NUM):
            f.write(f"# Start participant {i}\n")
            f.write(f"echo 'Starting participant {i}...'\n")
            f.write(f"nohup {exec_cmds[i + 1]} & \n")
            f.write(f"P{i}_PID=$!\n")
            f.write(f'echo "participant{i}:$P{i}_PID" >> {pids_file}\n')
            f.write("sleep 1\n\n")  # Small delay between participants

        # Start client after all nodes are running
        f.write("# Start client\n")
        f.write("echo 'Starting client...'\n")
        f.write(f"nohup {client_command} & \n")
        f.write(f"CLIENT_PID=$!\n")
        f.write(f'echo "client:$CLIENT_PID" >> {pids_file}\n\n')

        f.write("echo 'All nodes started. Check log files in logs directory.'\n")
        f.write("echo 'To stop all nodes, run: python3 setup.py close'\n")

    # Make the script executable
    os.chmod(bash_script_path, 0o755)

    # Execute the bash script
    print(f"Executing start script: {bash_script_path}")
    subprocess.call([bash_script_path])


def close_nodes():
    """
    Shut down all node processes and PostgreSQL instances by reading stored PIDs.
    """
    print("Shutting down all nodes and PostgreSQL instances...")

    # Kill processes using stored PIDs
    if os.path.exists(pids_file):
        try:
            with open(pids_file, "r") as f:
                for line in f:
                    if line.strip():
                        name, pid = line.strip().split(":")
                        print(f"Terminating {name} process (PID: {pid})")
                        try:
                            subprocess.run(["kill", pid], check=False)
                        except Exception as e:
                            print(f"Error killing process {pid}: {e}")

            # Remove the PID file after killing all processes
            os.unlink(pids_file)
        except Exception as e:
            print(f"Error processing PIDs file: {e}")
    else:
        print("No PID file found. Nodes may not be running.")

    # Wait a moment for processes to terminate
    time.sleep(2)

    # Shutdown PostgreSQL instances
    print("Shutting down PostgreSQL instances...")
    for i in range(NODES_NUM + 1):
        if i == NODES_NUM:
            PG_DATA_DIR = f"./coorddb"
            PGPORT = str(8890)
        else:
            PG_DATA_DIR = f"./node{i}db"
            PGPORT = str(8880 + i)

        try:
            result = subprocess.run(
                ["pg_ctl", "stop", "-D", PG_DATA_DIR],
                check=False,
                capture_output=True,
                text=True,
                env={**os.environ, "PGPORT": PGPORT},
            )
            if result.returncode == 0:
                print(f"PostgreSQL instance at {PG_DATA_DIR} stopped successfully")
            else:
                print(f"Failed to stop PostgreSQL at {PG_DATA_DIR}: {result.stderr}")
        except Exception as e:
            print(f"Error stopping PostgreSQL at {PG_DATA_DIR}: {str(e)}")

    print("All nodes and PostgreSQL instances have been shut down.")


def clean_nodes():
    """
    Clean up database directories by removing them completely.
    """
    print("Cleaning up database directories...")

    # Remove node databases
    for i in range(NODES_NUM):
        db_dir = f"./node{i}db"
        if os.path.exists(db_dir):
            try:
                subprocess.run(["rm", "-rf", db_dir], check=True)
                print(f"Removed database directory: {db_dir}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to remove {db_dir}: {e}")

    # Remove coordinator database
    coord_db_dir = "./coorddb"
    if os.path.exists(coord_db_dir):
        try:
            subprocess.run(["rm", "-rf", coord_db_dir], check=True)
            print(f"Removed database directory: {coord_db_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove {coord_db_dir}: {e}")

    print("All database directories have been removed.")


# Main script execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "close":
            close_nodes()
        elif sys.argv[1] == "clean":
            clean_nodes()
        elif sys.argv[1] == "close-clean":
            close_nodes()
            time.sleep(2)
            clean_nodes()
        elif sys.argv[1] == "clean-start":
            clean_nodes()
            time.sleep(2)
            startup()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available commands: close, clean, closeandclean")
    else:
        # No arguments, start up the nodes
        startup()
        print("Nodes have been started. To stop them, run: python setup.py close")
