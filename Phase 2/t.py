import threading
import time

def show():
    while True:
        time.sleep(1)
        print("....")

def t():
    threading.Thread(target=show).start()
    print("what is ur name")
    time.sleep(4)
    return

t()