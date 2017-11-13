'''
This class enables the programmer to interface with the _lockThread mechanism (servo)
'''
import threading
import queue
import time
import RPi.GPIO as GPIO
from Const import *
from multiprocessing import Process
from dbug import *

PARCEL = [True, "LOCKER"] # for debugging

class Lock():
    ''' This is a wrapper class utilizing the _LockThread '''
    def __init__(self):
        self._inQueue = queue.Queue() # Lock reads from this
        self._outQueue = queue.Queue() # Lock writes to this
        self._qL = [self._outQueue, self._inQueue] # thread reads from the _outQueue, writes to the _inQueue

        self.lThread = None # the lock thread
        self._startLockThread()

        # assume the lock is unlocked by default
        self.locked = False

        # start the sync thread
        a = threading.Thread(target=self._keepSync)
        a.start()

    def _startLockThread(self: 'Lock') -> None:
        ''' Start the lock thread '''
        if (self.lThread == None or not self.lThread.is_alive()):
            dbug(PARCEL, "starting lock thread")
            self.lThread = _lockThread(self._qL)
            self.lThread.start() # start the _lockThread thread

    def _keepSync(self: 'Lock') -> None:
        ''' Keep the variables in sync by listening to the input queue. '''

        while True:        
            # read queue data
            data = self._inQueue.get()
            if (data == ST_LOCKED):
                self.locked = True
            elif (data == ST_UNLOCKED):
                self.locked = False

    def lock(self: 'Lock') -> None:
        ''' Lock the lock '''
        self._outQueue.put(DO_LOCK)
        return

    def unlock(self: 'Lock') -> None:
        ''' Unlock the lock '''
        self._outQueue.put(DO_UNLOCK)
        return

    def isLocked(self: 'Lock') -> bool:
        ''' Return True if locked, false otherwise. '''
        return self.locked


class _lockThread(threading.Thread):
    ''' This is the thread on which the lock lives '''
    def __init__(self, queues):
        threading.Thread.__init__(self)

        dbug(PARCEL, "lockThread initializing")
        # set up GPIO
        self.servoPin = 21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servoPin, GPIO.OUT)

        self.p = GPIO.PWM(self.servoPin, 50)
        self.locked = False
        # this thread is used to move the servo
        self.servoMovementThread = None

        self.inQueue = queues[0] # to read from
        self.outQueue = queues[1] # to write to
        # lock the lock by default
        self._lock()

    def run(self):

        while True:
            data = self.inQueue.get()
            # process a command
            self._process_cmd(data)

        dbug(PARCEL, "lock thread finished")
        return           

    def _auto_lock_subroutine(self: '_lockThread', sleepTime: 'int', inQueue: 'Queue') -> None:
        ''' Wait sleepTime amount of time, then send a signal to parent thread (_lockThread) using the inQueue
        that time has passed 
        '''
        time.sleep(sleepTime)
        #inQueue.put(AUTO_LOCK) # signal to the locker thread, autolocker has waited time for auto _lockThread
        self._lock()
        return

    def _moveServoThread(self: '_lockThread', percentage: 'float') -> None:
        ''' Move the servo do a certain percentage
        
        REQ: percentage in range [0,1]
        '''
        pWidth = 2.5 + (10*percentage)
        dbug(PARCEL, ">moving... " + str(percentage * 100.0) + " wait...")
        self.p.start(pWidth)
        # wait some time to ensure servo completed movement
        time.sleep(2)

        dbug(PARCEL, "done moving, ready for lock/unlock")
        return

    def _moveServo(self: '_lockThread', percentage: 'float') -> None:
        ''' Move the servo to a given percentage value as float.

        REQ: percentage is a float value in [0,1]
        '''
        # halt until servo movement completed
        while self.servoMovementThread != None and self.servoMovementThread.isAlive():
            dbug(PARCEL, "blocking")
            pass
    
        self.servoMovementThread = threading.Thread(target=self._moveServoThread, args=(percentage,))
        self.servoMovementThread.start()

    def _unlock(self: '_lockThread') -> None:
        # unlock if locked
        if (self.locked):
            dbug(PARCEL, "unlocked")
            self._moveServo(1)
            self._write_back(ST_UNLOCKED)
            self.locked = False
            # start the countdown to auto lock
            t = threading.Thread(target=self._auto_lock_subroutine, args=(5, self.inQueue,))
            t.start()
        else:
            dbug(PARCEL, "already unlocked")

    def _lock(self):
        # lock if unlocked
        if (not self.locked):
            dbug(PARCEL, "locked")
            self._moveServo(2.5)
            # signal back to parent obj 
            self._write_back(ST_LOCKED)
            self.locked = True
        else:
            dbug(PARCEL, "already locked")

    def _write_back(self: '_lockThread', msg: 'str') -> None:
        self.outQueue.put(msg)     

    def _process_cmd(self: '_lockThread', cmd: 'str') -> None:
        ''' Process a command, and do the correct function, or put the correct value inside outQueue
        to be sent out to the main thread.

        REQ: cmd is a specific command handled by this function below.
        '''
      
        if (cmd == DO_LOCK):
            # lock command from main thread
            self._lock()
        elif (cmd == DO_UNLOCK):
            # unlock command from main thread
            self._unlock()

