# this is a Python3 file
import Threading
import time
import queue


class BT (threading.Thread):
    def __init__(self, q : queue):
        threading.Thread.__init__(self) 
        self.q = q = None # store the queue here to communicate with main thread
        self.cancelled = False
    def run(self):
        # main loop
        while True:
            # check for command
            if not self.q.empty():
                # process the command
                self._process_queue(q.get())
            else:
                # wait for BT comms
                print("reading bt...")

    def _process_queue(arg):
        '''  (argument) -> None
        Given an argument, process it
        '''
        print(arg)

    def cancel(self):


    def send(msg):
        ''' (str) -> None
        Send a message through bluetooth
        '''
        pass