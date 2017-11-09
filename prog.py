
from Locker import Lock
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

l = Lock()


a = threading.Thread(target=inp, args=(inpQueue,))
a.start()

print("main thread loop starts")
while True:   

    if (not inpQueue.empty()):
        data = inpQueue.get()
        
        if (data == "lock"):
            l.lock()
        elif (data == "unlock"):
            l.unlock()
        elif (data == "lockstats"):
            print(l.isLocked())
print("program ends")

