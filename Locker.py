'''
This class enables the programmer to interface with the _lockThread mechanism (servo)
'''
import threading
import queue
import time
from Constants.Const import *


class _lockThread(threading.Thread):
    ''' This is the thread on which the lock lives '''
    def __init__(self, queues):
        threading.Thread.__init__(self)

        self.inQueue = queues[0] # reading from queue
        self.outQueue = queues[1] # writing queue
        self._lock() # locked by default

    def run(self):
        while True:
            if (not self.inQueue.empty()):
                # process a command
                self._process_cmd(self.inQueue.get())

        return           

    def _auto_lock(self: '_lockThread', sleepTime: 'int', inQueue: 'Queue') -> None:
        ''' Wait sleepTime amount of time, then send a signal to parent thread (_lockThread) using the inQueue
        that time has passed 
        '''
        time.sleep(sleepTime)
        inQueue.put(AUTO_LOCK) # signal to the locker thread, autolocker has waited time for auto _lockThread
        return

    def _unlock(self: '_lockThread') -> None:
        # unlock
        print("unlocked")
        self._write_back(ST_UNLOCKED)
        t = threading.Thread(target=self._auto_lock, args=(5, self.inQueue,))
        t.start()

    def _lock(self):
        # lock
        print("locked")
        self._write_back(ST_LOCKED)

    def _write_back(self: '_lockThread', msg: 'str') -> None:
        self.outQueue.put(msg)     

    def _process_cmd(self: '_lockThread', cmd: 'str') -> None:
        ''' Process a command, and do the correct function, or put the correct value inside outQueue
        to be sent out to the main thread.

        REQ: cmd is a specific command handled by this function below.
        '''
        if (cmd == AUTO_LOCK):
            # automatically locked (timer completed)
            self._lock()
        elif (cmd == DO_LOCK):
            # lock command from main thread
            self._lock()
        elif (cmd == DO_UNLOCK):
            # unlock command from main thread
            self._unlock()

class Lock():
    ''' This is a wrapper class utilizing the _LockThread '''
    def __init__(self):
        self._inQueue = queue.Queue() # Lock reads from this
        self._outQueue = queue.Queue() # Lock writes to this
        self._qL = [self._outQueue, self._inQueue] # thread reads from the _outQueue, writes to the _inQueue

        self.lThread = None # the lock thread
        self._startLockThread()

        self.locked = False
        # check for lock status in a separate thread
        a = threading.Thread(target=self._keepSync)
        a.start()

    def _startLockThread(self: 'Lock') -> None:
        ''' Start the lock thread '''
        self.lThread = _lockThread(self._qL)
        self.lThread.start() # start the _lockThread thread

    def _keepSync(self: 'Lock') -> None:
        ''' Keep the variables in sync by listening to the input queue. '''

        while True:
            # ensure the lock thread is alive
            if (not self.lThread.isAlive()):
                self._startLockThread()
                print("started lock thread...")

            if (not self._inQueue.empty()):
                # read queue data
                data = self._inQueue.get()
                if (data == ST_LOCKED):
                    self.locked = True
                elif (data == ST_UNLOCKED):
                    self.locked = False

    def lock(self: 'Lock') -> None:
        ''' Lock the lock '''
        self._outQueue.put(DO_LOCK)

    def unlock(self: 'Lock') -> None:
        ''' Unlock the lock '''
        self._outQueue.put(DO_UNLOCK)

    def isLocked(self: 'Lock') -> bool:
        ''' Return True if locked, false otherwise. '''
        return self.locked
