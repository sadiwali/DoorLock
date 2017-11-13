# this is a python3 script

import os
import glob
import time
from bluetooth import *
from Const import *
from multiprocessing import Process
from multiprocessing import Queue
import threading
import logging
import queue
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')


PARCEL = [True, "BT"] # for debugging

class BtObj():
    def __init__(self):
        self.inQueue = Queue()
        self.outQueue = Queue()

        self._qL[self.outQueue, self.inQueue]
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

        if (self._btProc == None or not self._btProc.is_alive()):
            self._btProc = BtProc(self._qL)
            self._btProc.start()

    def send(self: 'BtObj', msg: 'str') -> None:
        ''' Send a message via bluetooth.
        TODO return result (fail or success)
        '''
        self.outQueue.put([MESSAGE, msg])

    def _keepSync(self: 'BtObj') -> None:
        ''' Process all signals from the bluetooth process '''
        data = self.inQueue.get()
        if (data == BTCONNECTED):
            self.isConnected = True
        elif (data == BT_DISCONNECTED):
            self.isConnected = False
            # kill the process
            
            # start the process again
            self._startBtProc()

        else:
            # not a signal, put to read later
            self.dataQueue.put(data)
        

    
        
class BtProc(Process):
    ''' The bluetooth process waits for a connection to,
    and maintains a connection to the device. '''

    def __init__(self, queues):
        Process.__init__(self, name="BT")
      
        self.inQueue = queues[0] # reads from this queue
        self.outQueue = queues[1] # writes to this queue

        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)
        self.client_sock = None
        self.client_info = None
        self.port = self.server_sock.getsockname()[1]

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        advertise_service(self.server_sock, "CircleBot", service_id=self.uuid,
                        service_classes=[self.uuid, SERIAL_PORT_CLASS],
                        profiles=[SERIAL_PORT_PROFILE])

        print("Waiting for connection on RFCOMM channel " + str(self.port))
        self.client_sock, self.client_info = self.server_sock.accept()

        print("Accepted connection from " + str(self.client_info))
        self.messagingQueue.put(BT_CONNECTED)

    def listenToDevice(self):

        while True:
            print("waiting...")

            try:
                data = self.client_sock.recv(1024)
                data = data.decode("utf-8")

                if len(data) == 0:
                    print('zero len data')
                    break
                print("received: " + str(data))
                self.messagingQueue.put(str(data))

                msgToSend = "relay: " + data
                self._send_message(msgToSend)

                print("sending: " + msgToSend)

            except IOError:
                print("Disconnected");
                break
            except KeyboardInterrupt:
                print("disconnected")
                self.client_sock.close()
                self.server_sock.close()
                print("all done")
                break
            except:
                self.client_sock.close()
                self.server_sock.close()
                break
        print("bt thread ends")
        self.outQueue.put(BT_DISCONNECTED) # bluetooth ends, signal
        return

    def _send_message(self: 'BtProc', msg: 'str') -> None:
        self.client_sock.send(str.encode(msg)) # send a message to the device

    def run(self):
        while True:
            # read signals from the bluetooth object (parent)
            data = self.inQueue.get()
            # process the signal
            self._process_command(data)

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
          dbug(PARCEL, "received : (" + str(cType) + ", " + str(msg)")")  
        
        print("command is " + cmd)


