# this is a python3 script

import os
import glob
import time
from bluetooth import *
from Const import *
from multiprocessing import Process
from multiprocessing import Queue
from dbug import *
import threading
import logging
import queue

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')


PARCEL = [True, "BT"] # for debugging

class BtObj():
    def __init__(self):
        self.inQueue = Queue() # to read from
        self.outQueue = Queue() # to write to

        self._qL = [self.outQueue, self.inQueue]
        self.dataQueue = queue.Queue() # stores data received from the connected device
        self.isConnected = False
        self._btProc = None
        # start the bluetooth process
        self._startBtProc()

        # start the infinite loop checking process signals
        t = threading.Thread(target=self._keepSync)
        t.start()

    def _startBtProc(self: "BtObj") -> None:
        ''' Start the bluetooth thread if it is not already started '''
        dbug(PARCEL, "starting bt THread")
        if (self._btProc == None):
            self._btProc = BtProc(self._qL)
            self._btProc.start()

            pass

    def send(self: 'BtObj', msg: 'str') -> None:
        ''' Send a message via bluetooth.
        TODO return result (fail or success)
        '''
        self.outQueue.put([MESSAGE, msg])

    def _keepSync(self: 'BtObj') -> None:
        ''' Process all signals from the bluetooth process '''
        while True:
            data = self.inQueue.get()
            if (data == BT_CONNECTED):
                self.isConnected = True
            elif (data == BT_DISCONNECTED):
                self.isConnected = False
                # kill the process
                dbug(PARCEL, "ends bt thread, start another one pls")
                self._btProc.join()
                # start the process again
                self._startBtProc()

            else:
                dbug(PARCEL, "putting: " + data)
                # not a signal, put to read later
                self.dataQueue.put(data)
        

    
        
class BtProc(Process):
    ''' The bluetooth process waits for a connection to,
    and maintains a connection to the device. '''

    def __init__(self, queues):
        Process.__init__(self, name="BT")
      
        self.inQueue = queues[0] # reads from this queue
        self.outQueue = queues[1] # writes to this queue
        self.cancelled = False
        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)
        self.client_sock = None
        self.client_info = None
        self.port = self.server_sock.getsockname()[1]

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        t = threading.Thread(target=self._initConnection)
        t.start()      

    def _initConnection(self):
        advertise_service(self.server_sock, "CircleBot", service_id=self.uuid,
                        service_classes=[self.uuid, SERIAL_PORT_CLASS],
                        profiles=[SERIAL_PORT_PROFILE])

        dbug(PARCEL, "Waiting for connection on RFCOMM channel " + str(self.port))
        self.client_sock, self.client_info = self.server_sock.accept()

        dbug(PARCEL, "Accepted connection from " + str(self.client_info))
        self.outQueue.put(BT_CONNECTED)
        self.listenToDevice()
        return

    def listenToDevice(self):

        while True:
            dbug(PARCEL, "waiting...")

            try:
                data = self.client_sock.recv(1024)
                data = data.decode("utf-8")

                if len(data) == 0:
                    dbug(PARCEL, 'zero len data')
                    break
                dbug(PARCEL, "received: " + data)
                self.outQueue.put(str(data))

                msgToSend = "relay: " + data
                # send back to connected device
                self._send_message(msgToSend)

                dbug(PARCEL, "sending back: " + msgToSend)

            except IOError:
                dbug(PARCEL, "Disconnected");
                break
            except KeyboardInterrupt:
                dbug(PARCEL, "disconnected")
                self.client_sock.close()
                self.server_sock.close()
                dbug(PARCEL, "all done")
                break
            except:
                dbug(PARCEL, "whats wrong")
                self.client_sock.close()
                self.server_sock.close()
                break
        dbug(PARCEL, "bt thread ends")

        self.outQueue.put(BT_DISCONNECTED) # bluetooth ends, signal
        self.cancelled = True
        dbug(PARCEL, "END BT PROC: " + str(self.cancelled))
  
        return

    def _send_message(self: 'BtProc', msg: 'str') -> None:
        self.client_sock.send(str.encode(msg)) # send a message to the device

    def run(self):
        dbug(PARCEL, "Started...........")
        while True and not self.cancelled:
            # read signals from the bluetooth object (parent)
            data = self.inQueue.get()
            # process the signal
            self._process_command(data)
        dbug(PARCEL, "CANCELLED.........")

    def _process_command(self: 'BtProc', data: '(int, str)') -> None:
        ''' Process the command received from the BT object.
        The command could be a status getter, or a request to write
        to connected device.
        '''
        cType = data[0]
        msg = data[1]

        if (cType == MESSAGE):
            self._send_message(msg)
        else:
          dbug(PARCEL, "received : (" + str(cType) + ", " + str(msg)+")")  
        
        dbug(PARCEL, "command is " + cmd)


