import RPi.GPIO as GPIO
import time
import queue
import threading
from copy import deepcopy
from Adafruit_CharLCD import Adafruit_CharLCD



class LcdThread(threading.Thread):

    lcd = None # this is the lcd to set
    PIN_BLT = None # backlight pin
    col = 0
    row = 0

    prev_type = -1
    curr_screen = []

    def __init__(self, queues):
        ''' Initialize the LCD display '''
        threading.Thread.__init__(self, name="LCD")

        self.inQueue = queues[0]
        self.outQueue = queues[1]

        # LCD PINS
        self.PIN_RS = 26 # RS pin of LCD
        self.PIN_E = 19 # enable pin of LCD
        self.PIN_DB = [13, 6, 5, 11] # data pins for LCD
        self.LCD_COL_SIZE = 2 # number of charactes available vertically on LCD
        self.LCD_ROW_SIZE = 16 # the number of characters available horizontally on LCD
        self.PIN_BLT = None

        self.DEF_MSG_LEN = 10 # the default space allocated for displaying a message on LCD

        self.PIN_LCD_BACKLIGHT = 20 # backlight pin for LCD
        self.lcd = Adafruit_CharLCD(self.PIN_RS, self.PIN_E,self. PIN_DB[0], self.PIN_DB[1], self.PIN_DB[2], self.PIN_DB[3], self.LCD_COL_SIZE, self.LCD_ROW_SIZE)

        self.col = self.LCD_COL_SIZE
        self.row = self.LCD_ROW_SIZE

        # fill current screen with empty
        for i in range(self.col * self.row):
            self.curr_screen.append(" ")

        # turn on the display
        if (self.PIN_BLT != None):
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PIN_BLT, GPIO.OUT)
            GPIO.output(self.PIN_BLT, 1)

    def run(self):
        while True:
            if (not self.inQueue.empty()):
                data = self.messagingQueue.get()
                self._write_message(data)

    def _update_osd(self, overlay):
        ''' update the screen with new overlays.
        For scrolling text, call multiple times with given data.
        '''
        print(str(len(overlay)))
        # only update 
        for i in range(len(overlay)):
            if self.curr_screen[i] != overlay[i]:
                a = int(i >= self.row)
                b = i % self.row
               
                self.lcd.set_cursor(b, a)
                self.lcd.message(overlay[i])
                self.curr_screen[i] = overlay[i]


    def _create_osd_layer(self, data, dType):
        ''' Create an overlay layer given data for the OSD '''

        new_screen = []
        for i in range(self.row * self.col):
            new_screen.append(" ")

        if dType == 1:
            # 10 character message
            print(str(len(new_screen))+ " and " + str(len(data)))
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

        # send command to update screen
        self._update_osd(new_screen)
        return new_screen

    def _new_message_scroll(self, message, length):
        ''' (str) -> list of list of str
        Return a list of list of strings for a full scroll effect

        REQ: len(message) > length
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


    def _clear(self):
        ''' clear the lcd '''
        self.lcd.clear()
        # clear screen in memory
        for i in range(self.col * self.row):
            self.curr_screen[i] = " "

    def _write_message(self, message):
        message_layers = self._new_message_scroll(message, 10)
        for i in range(len(message_layers)):
            osd_layer = self._create_osd_layer(message_layers[i], 1)
            self._update_osd(osd_layer) # display on screen
            time.sleep(0.5)
