
import Queue
import pscan
import httplib
import threading
import logging
import json
import time

from hardconf import *

class WeatherData:
    def __init__(self):
        self.outside = (0, None)
        self.home = (0, None)
        self.lock = threading.Lock()
        
    def setOutside(self, data):
        with self.lock:
            self.outside = (time.time(), data)
    
    def setInside(self, data):
        with self.lock:
            self.home = (time.time(), data)
            
    def getOutside(self, newerThan = 0):
        with self.lock:
            if self.outside[0] > newerThan:
                return (self.outside[0], self.outside[1].copy())
    
    def getInside(self, newerThan = 0):
        with self.lock:
            if self.home[0] > newerThan:
                return (self.home[0], self.home[1][:])
                
    def getData(self, newerThan = 0):
        with self.lock:
            if self.outside[0] > newerThan or self.home[0] > newerThan:
                ts = self.outside[0]
                if self.home[0] > ts:
                    ts = self.home[0]
                out = None
                ins = None
                if self.outside[1] is not None:
                    out = self.outside[1].copy()
                if self.home[1] is not None:
                    ins = self.home[1][:]
                return (ts, out, ins)
                
    def hasActualData(self):
        with self.lock:
            ts = self.outside[0]
            if self.home[0] > ts:
                ts = self.home[0]
        return (time.time() - ts) < 3600


def getWeatherThread(dataSink):
    try:
        conn = httplib.HTTPConnection('odroid', 8001, timeout=2)
        try:
            conn.request("GET", "/teraz")
            resp = conn.getresponse()
            if 200 == resp.status:
                text = resp.read()
                dataSink.setOutside(json.loads(text))
            else:
                raise Exception("Server responded with %d" % resp.status)
        finally:
            conn.close()
    except Exception as exc:
        logging.error("getWeatherThread: %s", exc)

def getHomeThread(dataSink):
    try:
        conn = httplib.HTTPConnection('odroid', 8000, timeout=2)
        try:
            conn.request("GET", "/actual")
            resp = conn.getresponse()
            if 200 == resp.status:
                text = resp.read()
                dataSink.setInside(json.loads(text))
            else:
                raise Exception("Server responded with %d" % resp.status)
        finally:
            conn.close()
    except Exception as exc:
        logging.error("getHomeThread: %s", exc)   
    


class PressHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("disturb")
        
W_S_START = 0
W_S_GET_OUT = 1
W_S_WAIT_IN = 2
W_S_GET_IN = 3
W_S_WAIT_OUT = 4

class WeatherLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.pressHandler = PressHandler(context)
        self.weatherData = WeatherData()
        self.getThread = None
        self.state = W_S_START
        self.ctr = 0
        self.ctx.weatherData = self.weatherData
        
    def open(self):
        if self.isOpen:
            return
        self.ctx.buttons.addHandler(self.pressHandler, BUT_TOP_LEFT)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_TOP_CENTER)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_TOP_RIGHT)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_MID_LEFT)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_MID_CENTER)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_MID_RIGHT)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_BOT_LEFT)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_BOT_CENTER)
        self.ctx.buttons.addHandler(self.pressHandler, BUT_BOT_RIGHT)
        
        ui = self.ctx.weather_ui
        ui.show()
        self.isOpen = True
        
    def cycle(self):
        try:
            msg = self.ctx.event_queue.get(timeout=.5)
            if msg == "disturb":
                return self.ctx.source_layer
        except Queue.Empty:
            pass
            
        if self.state == W_S_START:
            self.getThread = threading.Thread(target = getWeatherThread, kwargs = {'dataSink' : self.weatherData})
            self.getThread.start()
            self.state = W_S_GET_OUT
        elif self.state == W_S_GET_OUT:
            if not self.getThread.is_alive():
                self.ctr = 0
                self.state = W_S_WAIT_IN
        elif self.state == W_S_WAIT_IN:
            if self.ctr > 2:
                self.getThread = threading.Thread(target = getHomeThread, kwargs = {'dataSink' : self.weatherData})
                self.getThread.start()
                self.state = W_S_GET_IN
            self.ctr += 1
        elif self.state == W_S_GET_IN:
            if not self.getThread.is_alive():
                self.ctr = 0
                self.state = W_S_WAIT_OUT
        elif self.state == W_S_WAIT_OUT:
            if self.ctr > 20:
                self.state = W_S_START
            self.ctr += 1
        
        self.ctx.weather_ui.checkUpdate(self.weatherData)
            
            
    def close(self):
        self.isOpen = False
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_TOP_LEFT)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_TOP_CENTER)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_TOP_RIGHT)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_MID_LEFT)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_MID_CENTER)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_MID_RIGHT)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_BOT_LEFT)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_BOT_CENTER)
        self.ctx.buttons.removeHandler(self.pressHandler, BUT_BOT_RIGHT)
        ui = self.ctx.weather_ui
        ui.hide()
    