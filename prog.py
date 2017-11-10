
from Lcd import LcdThread
from Locker import Lock
from Const import *
import threading
import time
import queue
from multiprocessing import Queue


inpQueue = queue.Queue() # not multiprocessing queue
def inp(q):
    while True:
        print("enter input:")
        uInp = input()
        if (uInp != ""):
            q.put(uInp)



inQueue = Queue()
outQueue = Queue()
qL = [outQueue, inQueue]

lcd = LcdThread(qL)
lcd.start()



a = threading.Thread(target=inp, args=(inpQueue,))
a.daemon = True
a.start()

locker = Lock()



print("main thread loop starts")
while True:   


    data = inpQueue.get()
    if (data == 'lock'):
        locker.lock()
        pass    
    elif (data == 'unlock'):
        locker.unlock()
        pass
    else:
        # print to lcd
        outQueue.put(data)


        

print("program ends")

