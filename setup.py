import subprocess
import time

exec_cmds = []

coordinator = 'localhost:9000'
coordinator_db = 'localhost:8880'
participants = ['localhost:9001', 'localhost:9002']
participants_db = ['localhost:8881', 'localhost:8882']
script_path = '/Users/timur/PycharmProjects/two-phase-commit/main.py'  # Full path to main.py

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

print(exec_cmds)

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