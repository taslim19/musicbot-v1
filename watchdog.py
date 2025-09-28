import subprocess
import time

RESTART_DELAY = 5  # seconds

# Define the commands for both entrypoints
commands = [
    ["python", "-m", "DragMusic"],
    ["python", "server.py"]
]

processes = [None, None]

while True:
    # Start any process that isn't running
    for i, cmd in enumerate(commands):
        if processes[i] is None or processes[i].poll() is not None:
            print(f"[Watchdog] Starting: {' '.join(cmd)}")
            processes[i] = subprocess.Popen(cmd)
            time.sleep(1)  # Stagger startups slightly
    # Check every second if any process has exited
    time.sleep(1)
    for i, proc in enumerate(processes):
        if proc.poll() is not None:
            print(f"[Watchdog] Process {' '.join(commands[i])} exited. Restarting in {RESTART_DELAY} seconds...")
            time.sleep(RESTART_DELAY)
            processes[i] = None 