
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen

from gui_al import *
from hardconf import *
from ttt import get_text


class MenuPanel(QWidget):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.pos = 0
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
        qp.setPen(QPen(QColor.fromRgb(255,255,255), 3, 1, 0, 0x80))
        
        xpad, ypad, rec_w, rec_h, gap = self.autoSize()
        yoff = ypad
        
        for index, item in enumerate(SRC_ITEMS):
            qp.drawRect(xpad, yoff, rec_w, rec_h)
            
            if index == self.pos:
                qp.fillRect(xpad + 1, yoff + 1, rec_w - 2 , rec_h - 2, QColor.fromRgb(201, 148, 22))
                
            qp.drawText(xpad, yoff, rec_w, rec_h, 0x84, get_text(item))
            yoff += rec_h + gap
        
        qp.end()
        
    def autoSize(self):
        sw, sh = getScreenSize()
        ypad = int(0.1 * sh)
        recw = int(sw * 0.75)
        xpad = (sw - recw) / 2
        rech = int(((sh - 2 * ypad) / len(SRC_ITEMS)) * .8)
        gap = ((sh - 2 * ypad) / len(SRC_ITEMS)) - rech
        return xpad, ypad, recw, rech, gap
        
        
    def move(self, dy):
        self.pos = (self.pos + dy) % len(SRC_ITEMS)
        if self.pos < 0:
            self.pos = len(SRC_ITEMS) - self.pos
        self.update()
        
        
    def getPos(self):
        return self.pos

class SourceView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = MenuPanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()
        
    def move(self, dy):
        if self.widget is not None:
            self.widget.move(dy)

    def getPos(self):
        if self.widget is not None:
            return self.widget.getPos()
