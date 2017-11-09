# this is the main thread
import queue
import threading

from BluetoothComms import BComms
from Lcd import Lcd

class mainThread():
    def __init__(self):
        # queue which all threads write and read from
        # TODO each thread will have its own queue
        self.queue = queue.Queue()
        # list of all active threads (dead ones are removed)
        self.threads = []
        self._start_bt_thread()
        self._start_inp_thread()
        self._start_lcd_thread()
        self.btConnected = False

    def loop(self):
        ''' Main loop '''
        while True:
            # read the queue
            while not self.queue.empty():
                data = self.queue.get()
                if data == "BTCONNECTED":
                    self.btConnected = True
                    print("connected")
                elif "L_INP_" in data:
                    print_lcd(data)
                else: 
                    print("RECEIVED THIS: " + data + " queue size: " + str(self.queue.qsize()))
                
            # ensured bluetooth thread always running
            endInd = len(self.threads)
            currInd = 0
            while currInd < endInd:
                # remove dead threads
                if (not self.threads[currInd].isAlive()):
                    print("removing a dead thread")
                    self.threads[i].join()
                    del self.threads[i]
                    currInd -= 1
                    endInd -= 1

                    if (endInd <= 0):
                        print("ALL THREADS KILLED. Starting fresh with bluetoth...")
                        self._start_bt_thread()
                        continue

                if (self.threads[currInd].getName() != "BT" and currInd == (endInd - 1)):
                    # bluetooth thread was not found
                    self.btConnected = False
                    print("bluetooth thread closed. Starting new one...")
                    self._start_bt_thread()

                currInd += 1

    def _start_bt_thread(self):
        ''' Start the bluetooth thread '''
        # pass in the master queue
        t = BComms(self.queue)

        # add to list of threads managed
        self.threads.append(t)

        t.start()
        print("bluetooth thread successfully started.")

    def _start_inp_thread(self):
        t = threading.Thread(target=self.get_input, args=(self.queue,))
        self.threads.append(t)
        t.start()
    def _start_lcd_thread(self):
        t = Lcd(self.queue)
        self.threads.append(t)
        t.start()

    def print_lcd(self, data):
        self.queue.put("R_LCD_hello world")


    def get_input(self, q):
        while True:
            print("enter input")
            inp = input()
            q.put("L_INP_" + inp)



print("main program started---")
mT = mainThread()
mT.loop()
print("main program ended---")