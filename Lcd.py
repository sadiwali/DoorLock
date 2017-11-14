import RPi.GPIO as GPIO
import time
import threading
from copy import deepcopy
from Adafruit_CharLCD import Adafruit_CharLCD
from multiprocessing import Process
from multiprocessing import Queue

# debugging
from dbug import *
PARCEL = [True, "LCD"]

class LcdObj():
    ''' The wrapper class which wraps the LCD display process '''
    def __init__(self: 'LcdObj') -> None:
        ''' Initialize the LCD process, and keep it alive '''
        self.inQueue = Queue() # reading from
        self.outQueue = Queue() # writing to
        self._qL = [self.outQueue, self.inQueue]
        self._procLcd = None

        self._startLcdProc()
        # start the sync thread
        syncThread = threading.Thread(target=self._keepSync)
        syncThread.start()

    def _startLcdProc(self):
        ''' Start the process if does not exist, or dead '''
        if (self._procLcd == None or not self._procLcd.is_alive()):
            # if first time load, or process is dead
            dbug(PARCEL, "LCD process starting")
            self._procLcd = _LcdProc(self._qL)
            self._procLcd.start()

    def _keepSync(self):
        ''' Keep the thread in sync '''
        while True:
            # check messages from Lcd process
            data = self.inQueue.get()
            print("LCD sent: " + str(data))
            # LCD should not send back data

    def print(self, data: 'str') -> None:
        ''' Write a message to the LCD screen '''
        self.outQueue.put(data)


class _LcdProc(Process):
    ''' The process which manages the LCD output. '''
    def __init__(self, queues):
        ''' Initialize the LCD display '''
        Process.__init__(self, name="LCD")

        self.inQueue = queues[0] # to read from
        self.outQueue = queues[1] # to write to

        # LCD PINS
        self.PIN_RS = 26 # RS pin of LCD
        self.PIN_E = 19 # enable pin of LCD
        self.PIN_DB = [13, 6, 5, 11] # data pins for LCD
        self.LCD_COL_SIZE = 2 # number of charactes available vertically on LCD
        self.LCD_ROW_SIZE = 16 # the number of characters available horizontally on LCD
        self.PIN_BLT = None

        self.DEF_MSG_LEN = 10 # the default space allocated for displaying a message on LCD

        self.PIN_LCD_BACKLIGHT = 20 # backlight pin for LCD
        # the Adafruit LCD object
        self.lcd = Adafruit_CharLCD(self.PIN_RS, self.PIN_E,self. PIN_DB[0], self.PIN_DB[1], self.PIN_DB[2], self.PIN_DB[3], self.LCD_COL_SIZE, self.LCD_ROW_SIZE)

        self.curr_screen = []

        # fill current screen with empty
        for i in range(self.LCD_COL_SIZE * self.LCD_ROW_SIZE):
            self.curr_screen.append(" ")

        # turn on the display
        if (self.PIN_BLT != None):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PIN_BLT, GPIO.OUT)
            GPIO.output(self.PIN_BLT, 1)

    def run(self: '_LcdProc') -> None:
        ''' The main loop of the process waits for something to print, then prints it '''
        while True:
            # check for data to print
            data = self.inQueue.get()
            # start a new thread to print data to LCD
            t = threading.Thread(target=self._write_message, args=(data,))
            t.start()

    def _update_osd(self: '_LcdProc', overlay: '[str]') -> None:
        ''' Display the overlay on the LCD sccreen. Given overrlay which is a list of characters
        for each position of the lcd screen, Loop through each character, and write to the 
        correct position in the LCD screen individually.

        REQ: len(overlay) is even
        REQ: each item in overlay is a single character
        '''
        # only update 
        for i in range(len(overlay)):
            if self.curr_screen[i] != overlay[i]:
                # do if the current character is different from the overlay character at this position
                row = int(i >= self.LCD_ROW_SIZE)
                col = i % self.LCD_ROW_SIZE
               
                # set the position of the cursor, and write a character
                self.lcd.set_cursor(col, row)
                self.lcd.message(overlay[i])
                # remember the state of the current screen
                self.curr_screen[i] = overlay[i]


    def _create_osd_layer(self: '_LcdProc', data: 'str', dType: 'int') -> [str]:
        ''' Given the data, and a type, return an overlay layer which is a list of 
        characters in positions corresponding to the position of each pixel. Depending on the type,
        the characters will be positioned differently. Data can be positioned in any programed position below.
        
        REQ: data is a string of characters
        REQ: dType an int that is handled below 
        '''

        new_screen = []
        # clear the screen layer
        for i in range(self.LCD_ROW_SIZE * self.LCD_COL_SIZE):
            new_screen.append(" ")

        if dType == 1:
            # 10 character message
            dbug(PARCEL, str(len(new_screen))+ " and " + str(len(data)))
            for i in range(len(data)):
                new_screen[i] = data[i]

        elif dType == 2:
            # temperature top right (print from right to left)
            new_screen[15] == "C"
            new_screen[14] == "°"
            if len(data) == 1:
                # single digit temperatures
                new_screen[13] == data
            elif len(data) == 2:
                # double digit temperatures
                new_screen[12] == data[0]
                new_screen[13] == data[1]

        return new_screen

    def _new_message_scroll(self: '_LcdProc', message: 'str', length: 'int') -> [[str]] :
        ''' Given a message, create a list of overlays to be displayed on LCD screen.
        If the message is less than the given length, create ony one layer, or one list
        of list of characters. Otherwise, create enough layers for there to be a full loop 
        cycle of the string printed.
        '''
        full_scroll_arr = [] # contains list of list of strings for full scroll
        lcd_arr = [] # contains the current scroll

        # if message shorter than or equal to 16 characters, no need to scroll
        if (len(message) <= length):
            for i in range(len(message)):
                lcd_arr.append(message[i])
            
            full_scroll_arr.append(lcd_arr)
            return full_scroll_arr

        # add extra spaces so tail is not connected to head while scrolling
        message += "  "

        # populate the char_arr with whitespace
        for i in range(length):
            lcd_arr.append(" ")

        # populate with content
        for i in range(len(message) + 1):
            a = 0
            for j in range(i, i + length):            
                k = j
                if (j >= len(message)):
                    k = j - len(message)
            
                lcd_arr[a] = message[k]
                a+=1
            # remember the scroll instance
            full_scroll_arr.append(deepcopy(lcd_arr))

        # return all scroll instances for full scroll effect
        return full_scroll_arr


    def _clear(self: '_LcdProc') -> None:
        ''' Clear the LCD screen, along with the overlay in memory. '''
        self.lcd.clear()
        # clear screen in memory
        for i in range(self.LCD_COL_SIZE * self.LCD_ROW_SIZE):
            self.curr_screen[i] = " "

    def _write_message(self: '_LcdProc', message: 'str') -> None:
        ''' Given a message, write the message to screen. '''

        message_layers = self._new_message_scroll(message, 10)
        for i in range(len(message_layers)):
            start = time.time()
            osd_layer = self._create_osd_layer(message_layers[i], 1)
            self._update_osd(osd_layer) # display on screen
            dbug(PARCEL, time.time() - start)
            time.sleep(0.5)
        dbug(PARCEL, "---------------------------------")
        return
