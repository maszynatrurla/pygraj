
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

from gui_al import *

class PodPanel(QWidget):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(255, 255, 0))
        
        qp.end()


class PodView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = PodPanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()


