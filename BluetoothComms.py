# this is a python3 script

import os
import glob
import time
from bluetooth import *
import multiprocessing
import threading
import logging
import queue
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

class BComms(threading.Thread):


    def __init__(self, msgQueue):
        threading.Thread.__init__(self, name="BT")
      
        self.messagingQueue = msgQueue # master queue

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
        self.messagingQueue.put("BTCONNECTED")


    def send_message(self, msg):
        self.client_sock.send(str.encode(msg))

    def run(self):

        while True:
            # process any commands available
            if (not self.messagingQueue.empty()):
                #self._process_command(self.messagingQueue.get())
                pass
            else:
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
                    self.send_message(msgToSend)

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
        return

    def _process_command(self, cmd):
        if ("R_BT_" in cmd):
            print("GOT COMMAND DONT KNOW WHAT TO DO")
        else:
            self.messagingQueue.put(cmd)
        
        print("command is " + cmd)