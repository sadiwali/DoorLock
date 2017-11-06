# this is a python3 file
import time
import queue
q = Queue()
from rpi_main import BT


def main_program():
    print("Type 1 to start the thread...")
    # block until input
    inp = input()
    if (inp == "1"):
        t = BT()
        t.start()



if __name__ == "__main__":
    main_program()