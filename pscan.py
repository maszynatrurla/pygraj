#!/usr/bin/env python

import os
import time
import threading

from psztyk import *

BUTTON_COUNT = 9

def getPresses():
    pressed = []
    for button in range(9):
        value = psztyk_get(button)
        if "0" == value.strip():
            pressed.append(button)
    return pressed
    
    
class CzypiskHandler:
    
    def onPress(self, button):
        pass
        
    def onRelease(self, button):
        pass
        
    def onClick(self, button):
        pass
        
    def onLongPress(self, button):
        pass
    
class Czypiski:
    
    def __init__(self, handler):
        psztyk_init()
        self.intFp = os.open(gpio_file(GPIO_INT, "value"), os.O_RDONLY)
        self.handler = handler
        if self.intFp < 0:
            raise Exception("open file error")
    
    def dispatch(self):
        os.lseek(self.intFp, 0, os.SEEK_SET)
        value = os.read(self.intFp, 6).strip()
        if "0" == value:
            self.handler(getPresses())
                
    def close(self):
        os.close(self.intFp)
        
class Czypisk:
    
    LONG_PRESS_TIME = 1
    LONG_PRESS_TIME_2 = 0.5
    
    STATE_IDK = 0
    STATE_PRESSED = 1
    STATE_LONG_PRESSED = 2
    STATE_RELEASED = 3
    
    def __init__(self, id):
        self.handlers = []
        self.pressedTs = 0
        self.id = id
        self.state = Czypisk.STATE_RELEASED

    def addHandler(self, handler):
        self.handlers.append(handler)
        
    def removeHandler(self, handler):
        self.handlers.remove(handler)
        
    def setPressed(self):
        if self.state == Czypisk.STATE_PRESSED:
            nowts = time.time()
            if nowts - self.pressedTs > Czypisk.LONG_PRESS_TIME:
                self.state = Czypisk.STATE_LONG_PRESSED
                self.pressedTs = nowts
                self.longPressEvt()
        elif self.state == Czypisk.STATE_LONG_PRESSED:
            nowts = time.time()
            if nowts - self.pressedTs > Czypisk.LONG_PRESS_TIME_2:
                self.pressedTs = nowts
                self.longPressEvt()
        elif self.state == Czypisk.STATE_RELEASED:
            self.state = Czypisk.STATE_PRESSED
            self.pressEvt()
            
    def setReleased(self):
        if self.state == Czypisk.STATE_PRESSED:
            self.releaseEvt()
            self.clickEvt()
        elif self.state == Czypisk.STATE_LONG_PRESSED:
            self.releaseEvt()
        self.state = Czypisk.STATE_RELEASED
        
    def longPressEvt(self):
        for hdl in self.handlers:
            hdl.onLongPress(self.id)
            
    def pressEvt(self):
        self.pressedTs = time.time()
        for hdl in self.handlers:
            hdl.onPress(self.id) 

    def releaseEvt(self):
        for hdl in self.handlers:
            hdl.onRelease(self.id) 
            
    def clickEvt(self):
        for hdl in self.handlers:
            hdl.onClick(self.id) 
        
class CzypiskThread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.goOn = True
        self.buttons = [Czypisk(id) for id in xrange(BUTTON_COUNT)]
        self.somethingWasPressed = False
        
    def addHandler(self, handler, buttonId = None):
        if buttonId is None:
            for but in self.buttons:
                but.addHandler(handler)
        else:
            self.buttons[buttonId].addHandler(handler)
            
    def removeHandler(self, handler, buttonId = None):
        if buttonId is None:
            for but in self.buttons:
                but.removeHandler(handler)
        else:
            self.buttons[buttonId].removeHandler(handler)
        
    def run(self):
        czypiski = Czypiski(None)
        
        while self.goOn:
            if self.somethingWasPressed:
                presses = getPresses()
                self.consumePresses(presses)
                if not presses:
                    self.somethingWasPressed = False
            else:
                os.lseek(czypiski.intFp, 0, os.SEEK_SET)
                value = os.read(czypiski.intFp, 6).strip()
                if "0" == value:
                    self.somethingWasPressed = True
                    presses = getPresses()
                    self.consumePresses(presses)
                    
            time.sleep(.05)
        
        czypiski.close()
        
    def consumePresses(self, presses):
        for id in xrange(BUTTON_COUNT):
            if id in presses:
                self.buttons[id].setPressed()
            else:
                self.buttons[id].setReleased()
                            
        
    def stop(self):
        self.goOn = False
    

def test_handler(presses):
    print(" + ".join(str(button) for button in presses))

def main():
    pszy = Czypiski(test_handler)
    
    try:
        while True:
            pszy.dispatch()
            time.sleep(.1)
    except KeyboardInterrupt:
        pass
    finally:
        pszy.close()
    
    psztyk_init()

if __name__ == "__main__":
    main()
