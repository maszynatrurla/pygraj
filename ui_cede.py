
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import QPoint, QRect

from gui_al import *

class CedePanel(QWidget):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)

    def autoSize(self):
        sw, sh = getScreenSize()
        tl = len(self.playlist.tracks)
        div = sh / tl
        if div > 80:
            return (80, 40)
        elif div < 12:
            return (12, 10)
        elif div < 14:
            return (div, 10)
        elif div < 20:
            return (div, 12)
        elif div < 25:
            return (div, 18)
        elif div < 30:
            return (div, 20)
        elif div < 35:
            return (div, 20)
        elif div < 45:
            return (div, 20)
        else:
            return (div, 20)
            
    def setPlaylist(self, playlist):
        self.playlist = playlist

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
                
        if len(self.playlist.tracks):
            
            qp.setPen(QPen(QColor.fromRgb(255, 255, 255)))
            
            rowSize, textSize = self.autoSize()
            qp.setFont(QFont("DejaVu Serif", textSize))
            
            pos = 1
            for idx, title, tlen in self.playlist.tracks:
                if pos == self.playlist.position:
                    qp.fillRect(0, (pos - 1) * rowSize, sw, rowSize, QColor.fromRgb(201, 148, 22))
                    qp.drawText(QRect(0, (pos - 1) * rowSize + 3, sw, rowSize), 0x1000, title)
                else:
                    qp.drawText(QRect(0, (pos - 1) * rowSize + 3, sw, rowSize), 0x1000, title)
                pos += 1
        
        qp.end()

class CedeView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = CedePanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
    def show(self):
        self.ctx.playlist.setWidget(self.widget)
        self.widget.setPlaylist(self.ctx.playlist)
        self.widget.show()
        
    def hide(self):
        self.widget.hide()
