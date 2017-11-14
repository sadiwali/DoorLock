
from Lcd import LcdObj
from Locker import Lock
from BluetoothComms import BtObj
from Const import *
import threading
import time
import queue
from multiprocessing import Queue
from dbug import *
PARCEL = [True, "prog"]


inpQueue = queue.Queue() # not multiprocessing queue
def inp(q):
    while True:
        print("enter input:")
        uInp = input()
        if (uInp != ""):
            q.put(uInp)

def btListenThread():
    dbug(PARCEL, "starts listening in prog")
    while True:
        data = bt.dataQueue.get()
        dbug(PARCEL, data)
        lcd.print(data)
        if (data == "DO_LOCK"):
            locker.lock()
        elif (data == "DO_UNLOCK"):
            locker.unlock()



a = threading.Thread(target=inp, args=(inpQueue,))
a.daemon = True
a.start()

locker = Lock()
bt = BtObj()
t = threading.Thread(target=btListenThread)
t.start()

lcd = LcdObj()

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
        lcd.print(data)






        

print("program ends")

