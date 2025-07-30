import subprocess
import time
import os
import sys
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Root directory of the project

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print("=== BASE_DIR ===", BASE_DIR)
for entry in os.listdir(BASE_DIR):
    print(" ENTRY:", entry)
sys.stdout.flush()


print("=== BASE_DIR:", BASE_DIR)
print("Contents of BASE_DIR:")
for e in os.listdir(BASE_DIR):
    print(" ", e)
lib_dir = os.path.join(BASE_DIR, "libraryDB")
print("Contents of libraryDB/:")
if os.path.isdir(lib_dir):
    for e in os.listdir(lib_dir):
        print("  -", e)
else:
    print("  ! libraryDB directory not found")
sys.stdout.flush()


# Use the current Python executable for all scripts
PYTHON = sys.executable

# Helper to build a command using the system Python
def py_cmd(script_path):
    return [PYTHON, os.path.join(BASE_DIR, script_path)]

# Define each service's startup command
commands = {
    "chatbot": [PYTHON, "-m", "uvicorn", "chatbot.chatbot:app", "--reload", "--host", "0.0.0.0"],
    "lost_items": py_cmd("lost_items/lost_items_api.py"),
    "verification_API": py_cmd("verification/verification_API.py"),
    "career_guidance": py_cmd("academic-career-guidance/ac-guide-AI.py"),
    "librarydb": py_cmd("libraryDB/librarydb.py"),
    "librarydb_ext": py_cmd("libraryDB/librarydb_ext.py"),
}

processes = {}

# Start a process and track it
def start_process(name, cmd):
    print(f"[{name}] Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes[name] = proc
    return proc

# Stop a running process
def stop_process(name):
    proc = processes.get(name)
    if proc and proc.poll() is None:
        print(f"[{name}] Stopping...")
        proc.terminate()
        proc.wait()

# Restart a service
def restart_process(name, cmd):
    stop_process(name)
    time.sleep(1)
    start_process(name, cmd)

# Watchdog handler to restart on file changes
class ChangeHandler(FileSystemEventHandler):
    def __init__(self, monitored_files):
        self.monitored_files = monitored_files

    def on_modified(self, event):
        for name, files in self.monitored_files.items():
            if any(event.src_path.endswith(f) for f in files):
                print(f"[{name}] Change detected in {event.src_path}, restarting...")
                restart_process(name, commands[name])
                break

# Set up file watchers
def watch_files(monitored_files):
    event_handler = ChangeHandler(monitored_files)
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=True)
    observer.start()
    return observer

# Monitor processes and auto-restart on exit
def monitor_processes():
    while True:
        for name, proc in processes.items():
            if proc.poll() is not None:
                print(f"[{name}] Process exited unexpectedly. Restarting...")
                restart_process(name, commands[name])
        time.sleep(2)

# Files to watch for each service
monitored_files = {
    "chatbot": ["chatbot/chatbot.py"],
    "lost_items": ["lost_items/lost_items_api.py"],
    "career_guidance": ["academic-career-guidance/ac-guide-AI.py"],
    "verification_API": ["verification/verification_API.py"],
    "librarydb": ["libraryDB/librarydb.py"],
    "librarydb_ext": ["libraryDB/librarydb_ext.py"],
}

# Launch all services
for name, cmd in commands.items():
    start_process(name, cmd)
    time.sleep(0.5)

# Start watchers and monitor thread
observer = watch_files(monitored_files)
monitor_thread = Thread(target=monitor_processes, daemon=True)
monitor_thread.start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down all processes...")
    observer.stop()
    for name in list(processes.keys()):
        stop_process(name)
    observer.join()
