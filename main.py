import os
import signal
import time
from dotenv import load_dotenv

from database import init_db
from util_funcs import graceful_exit

load_dotenv()

if __name__ == "__main__":
    print("[!] Starte Anima-Webplattform... (drücke STRG+C zum Beenden)")
    init_db()

    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    while True:
        try:
            print("Running")
        except Exception as e:
            print("[!] Fehler:", e)
        time.sleep(int(os.getenv("CHECK_INTERVALL")))
