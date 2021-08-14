
import time
from random import randint

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtCore import QRect

from gui_al import *

def prepareOutData(data):
    out = {}
    now = time.time()
    for k in ("solar_mv", "temperature", "humidity", "pressure", "pm1_0", "pm2_5", "pm10"):
        latest = data.get(k, {}).get("latest")
        ts = latest.get("ts", 0)
        if ts <= now and (now - ts) < 7200:
            out[k] = latest.get("value")
    return out
        
def prepareInData(data):
    out = [(None, None)]*4
    now = time.time()
    for g in data:
        id = g.get("gniot_id", 0) - 1
        if id >= 0 and id < 4:
            ts = g.get("ts", 0)
            if ts <= now and (now - ts) < 3600:
                out[id] = (g.get("T"), g.get("RH"))
    return out
        

class WeatherPanel(QWidget):
    
    def __init__(self, parent, controller):
        QWidget.__init__(self, parent)
        self.ctrl = controller
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
        
        if self.ctrl.outData is None and self.ctrl.inData is None:
            self.paintTimer(qp)
            
        else:
            if self.ctrl.outData:
                self.paintOutside(qp, prepareOutData(self.ctrl.outData))
                insideYoffset = int(0.75 * sh)
            else:
                insideYoffset = 0
                
            if self.ctrl.inData:
                self.paintInside(qp, prepareInData(self.ctrl.inData), insideYoffset)
        
        qp.end()
        
    def paintTimer(self, qp):
        sw, sh = getScreenSize()
        text = time.strftime("%d %B %H:%M")
        fnt = QFont("DejaVu Serif", 30)
        qp.setFont(fnt)
        qp.setPen(QPen(QColor.fromRgb(255, 255, 255)))
        
        fm = QFontMetrics(fnt)
        tw = fm.width(text)
        th = fm.height()
        
        x = randint(20, sw - 20 - tw)
        y = randint(20 + th, sh - 20)
        
        qp.drawText(x, y, text)
        
    def paintOutside(self, qp, data):
        self.paintSun(qp, data.get("solar_mv"))
        
        qp.setPen(QPen(QColor.fromRgb(255, 255, 255)))
        temp = data.get("temperature")
        if temp is not None:
            qp.setFont(QFont("DejaVu Sans", 90))
            qp.drawText(190, 190, u"%.1f\u00B0C" % temp)
            
        qp.setFont(QFont("DejaVu Sans", 32))
        rh = data.get("humidity")
        if rh is not None:
            qp.drawText(190, 250, "%.1f%%" % rh)
        pres = data.get("pressure")
        if pres is not None:
            qp.drawText(390, 250, "%.1f hPa" % pres)
            
        qp.setFont(QFont("DejaVu Sans", 12))
        qp.setPen(QPen(QColor.fromRgb(0x99, 0x99, 0x99)))
        pm1 = data.get("pm1_0")
        if pm1 is not None:
            qp.drawText(30, 320, "PM1.0")
        pm2 = data.get("pm2_5")
        if pm2 is not None:
            qp.drawText(306, 320, "PM2.5")
        pm10 = data.get("pm10")
        if pm10 is not None:
            qp.drawText(552, 320, "PM10")
        qp.setFont(QFont("DejaVu Sans", 30))
        if pm1 is not None:
            qp.drawText(90, 320, str(pm1))
        if pm2 is not None:
            qp.drawText(366, 320, str(pm2))
        if pm10 is not None:
            qp.drawText(612, 320, str(pm10))
        
        
    def paintSun(self, qp, value):
        qp.setPen(QPen(QColor.fromRgb(0, 0, 0)))
        if value is None:
            qp.setBrush(QColor.fromRgb(0xCC, 0xCC, 0xCC))
        elif value > 100 and value < 800:
            qp.setBrush(QColor.fromRgb(0xFF, 0xCC, 0x00))
        elif value >= 800:
            qp.setBrush(QColor.fromRgb(0xFF, 0xFF, 0x00))
        else:
            qp.setBrush(QColor.fromRgb(0xCC, 0xCC, 0xCC))
        qp.drawEllipse(35, 35, 113, 113)
        
        if value is not None:
            fnt = QFont("Liberation Mono", 18)
            qp.drawText(QRect(40, 80, 103, 22), 0x84, "%d mV" % value)
        
        
    def paintInside(self, qp, data, yOffset):
        sw, sh = getScreenSize()
        qp.setPen(QPen(QColor.fromRgb(255, 255, 255)))
        qp.setFont(QFont("DejaVu Sans", 32))
        xoff = 20
        for T, RH in data:
            if T is not None:
                qp.drawText(xoff, yOffset + 40, u"%d\u00B0C" % int(round(T)))
            xoff += (sw - 40) / 4
        qp.setPen(QPen(QColor.fromRgb(0x99, 0x99, 0x99)))
        qp.setFont(QFont("DejaVu Sans", 30))
        xoff = 20
        for T, RH in data:
            if T is not None:
                qp.drawText(xoff, yOffset + 82, u"%d%%" % RH)
            xoff += (sw - 40) / 4


class WeatherView:
    
    def __init__(self, context):
        self.ctx = context
        self.updateTime = 0
        self.outData = None
        self.inData = None
        self.timerTime = 0
        
    def construct(self, parent):
        self.widget = WeatherPanel(parent, self)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()

    def checkUpdate(self, weatherData):
        newData = weatherData.getData(self.updateTime)
        if newData is not None:
            self.updateTime, self.outData, self.inData = newData
            self.widget.update()
        else:
            now = time.time()
            if now - self.timerTime > 5:
                self.timerTime = now
                self.widget.update()
            
