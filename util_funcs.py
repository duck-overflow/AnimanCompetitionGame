import os
import signal
import sys

from os import listdir

def graceful_exit(signum, frame):
    print(f"\n[!] Signal {signum} empfangen. Beende das Programm sauber...")
    sys.exit(0)

def delete_sessions():
    sessionPath = "flask_session/"
    for file_name in listdir(sessionPath):
        os.remove(sessionPath + file_name) 