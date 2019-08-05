
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

from gui_al import *

class NetradioPanel(QWidget):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.title = ""
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(QColor.fromRgb(255,255,255), 3, 1, 0, 0x80))
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
        
        qp.setFont(QFont("DejaVu Serif", 20))
        qp.drawText(10, 10, sw - 20, sh - 20, 0x1084, self.title)
        
        qp.end()


class NetradioView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = NetradioPanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()
        
    def update(self, title):
        if title != self.widget.title:
            self.widget.title = title
            self.widget.update()
