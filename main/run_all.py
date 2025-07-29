import subprocess
import time
import os
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def pyenv_cmd(script_path):
    return [
        os.path.join(BASE_DIR, "myenv", "Scripts", "python.exe"),
        os.path.join(BASE_DIR, script_path)
    ]

commands = {
    "chatbot": ["uvicorn", "chatbot.chatbot:app", "--reload"],
    "lost_items": pyenv_cmd("lost_items/lost_items_api.py"),
    "verification_API": pyenv_cmd("verification/verification_API.py"),
    "career_guidance": ["uvicorn", "academic-career-guidance.ac-guide-AI:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
    "libraryDB": pyenv_cmd("libraryDB/libraryDB.py"),
    "libraryDB-ext": pyenv_cmd("libraryDB/libraryDB-ext.py"),
    "assessment_api": pyenv_cmd("Academic_Guidance_scripts/assessment_api.py"),
    "academic_planning_api": pyenv_cmd("Academic_Guidance_scripts/academic_planning_api.py"),
}

processes = {}

def start_process(name, cmd):
    print(f"[{name}] Starting: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=BASE_DIR)
    processes[name] = proc

def stop_process(name):
    proc = processes.get(name)
    if proc and proc.poll() is None:
        print(f"[{name}] Stopping...")
        proc.terminate()
        proc.wait()

def restart_process(name, cmd):
    stop_process(name)
    time.sleep(1)
    start_process(name, cmd)

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, monitored_files):
        self.monitored_files = monitored_files

    def on_modified(self, event):
        for name, files in self.monitored_files.items():
            if any(event.src_path.endswith(f) for f in files):
                print(f"[{name}] Change detected in {event.src_path}, restarting...")
                restart_process(name, commands[name])
                break

def watch_files(monitored_files):
    event_handler = ChangeHandler(monitored_files)
    observer = Observer()
    observer.schedule(event_handler, BASE_DIR, recursive=True)
    observer.start()
    return observer

def monitor_processes():
    while True:
        for name, proc in processes.items():
            if proc.poll() is not None:
                print(f"[{name}] Process exited unexpectedly. Restarting...")
                restart_process(name, commands[name])
        time.sleep(2)

monitored_files = {
    "chatbot": ["chatbot/chatbot.py"],
    "lost_items": ["lost_items/lost_items_api.py"],
    "career_guidance": ["academic-career-guidance/ac-guide-AI.py"],
    "verification_API": ["verification/verification_API.py"],
    "libraryDB": ["libraryDB/libraryDB.py"],
    "libraryDB-ext": ["libraryDB/libraryDB.py"],
    "assessment_api": ["Academic_Guidance_scripts/assessment_api.py"],
    "academic_planning_api": ["Academic_Guidance_scripts/academic_planning_api.py"]
}

for name, cmd in commands.items():
    start_process(name, cmd)
    time.sleep(1)

observer = watch_files(monitored_files)

monitor_thread = Thread(target=monitor_processes, daemon=True)
monitor_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down all processes...")
    observer.stop()
    for name in list(processes.keys()):
        stop_process(name)
    observer.join()
