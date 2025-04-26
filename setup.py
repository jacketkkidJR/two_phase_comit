import os
import subprocess
import time

NODES_NUM = 10  # Represents the number of nodes. Should be no more than 10

SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

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
    
    time.sleep(3)

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

exec_cmds = []

coordinator = 'localhost:9010'
coordinator_db = 'localhost:8890'
participants = []
participants_db = []
for i in range(NODES_NUM):
    participants.append(f'localhost:900{i}')
    participants_db.append(f'localhost:888{i}')

script_path = os.path.join(SETUP_DIR, "main.py")

coordinator_setup_command = f'python3 {script_path} --host {coordinator}'
for participant in participants:
    coordinator_setup_command += f' --participant {participant}'
coordinator_setup_command += ' --log-db logcoord'
coordinator_setup_command += f' --log-db-host {coordinator_db}'
coordinator_setup_command += f" --batch-size {len(participants)}"

exec_cmds.append(coordinator_setup_command)

for i, participant in enumerate(participants):
    participant_setup_command = f'python3 {script_path} --node-id {i} --host {participant} --coordinator {coordinator} --log-db lognode{i} --log-db-host {participants_db[i]} --data-db datanode{i} --data-db-host {participants_db[i]}'
    exec_cmds.append(participant_setup_command)

def escape_for_applescript(cmd):
    """
    Escapes a string to be safely embedded in AppleScript/osascript commands.
    """
    # First, escape backslashes
    cmd = cmd.replace('\\', '\\\\')
    # Then, escape double quotes
    cmd = cmd.replace('"', '\\"')
    return cmd

def run_in_new_tab(cmd):
    """
    Uses AppleScript to open a new Terminal tab and run the command.
    """
    escaped_cmd = escape_for_applescript(cmd)
    # AppleScript: open a new tab, then run the command in that tab
    applescript = f'''
osascript <<END
tell application "Terminal"
    activate
    tell application "System Events" to keystroke "t" using command down
    delay 0.2
    do script "{escaped_cmd}" in selected tab of the front window
end tell
END
'''
    # Run the AppleScript
    subprocess.Popen(applescript, shell=True)

# Open the first tab (Terminal always opens with one tab)
# So, run the first command in the current tab, then open new tabs for the rest
if exec_cmds:
    # First command goes in the first tab
    escaped_cmd = escape_for_applescript(exec_cmds[0])
    applescript = f'''
osascript <<END
tell application "Terminal"
    activate
    do script "{escaped_cmd}" in front window
end tell
END
'''
    subprocess.Popen(applescript, shell=True)
    # Give Terminal a moment to open and run the command
    time.sleep(1)

    # The rest go in new tabs
    for cmd in exec_cmds[1:]:
        run_in_new_tab(cmd)
        time.sleep(1)  # Small delay to avoid race conditions

client_path = os.path.join(SETUP_DIR, "client.py")
client_command = f'python3 {client_path} --coordinator {coordinator} --demo thermometerobservation --n-nodes {NODES_NUM}'

# Run the client command in a new tab
run_in_new_tab(client_command)