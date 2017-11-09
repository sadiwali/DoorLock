
from Lcd import LcdThread
from Const import *
import threading
import time
import queue

inpQueue = queue.Queue()
def inp(q):
    while True:
        print("enter input:")
        uInp = input()
        if (uInp != ""):
            q.put(uInp)


inQueue = queue.Queue()
outQueue = queue.Queue()
qL = [outQueue, inQueue]

lcd = LcdThread(qL)
lcd.start()



a = threading.Thread(target=inp, args=(inpQueue,))
a.start()

print("main thread loop starts")
while True:   

    if (not inpQueue.empty()):
        data = inpQueue.get()
        outQueue.put(data)
        

print("program ends")

