
from PyQt5.QtGui import QColor, QFont

class ArtistListHandler:
    
    def __init__(self):
        self.focused = False
        
    def calculateSize(self, item):
        return (0, 28)
        
    def preparePainter(self, qp):
        qp.setFont(QFont("DejaVu Serif", 14))
        
    def focus(self):
        self.focused = True
        
    def unfocus(self):
        self.focused = False
        
    def paint(self, item, qp, x, y, w, h):
        if item.is_selected:
            if self.focused:
                qp.fillRect(1, y, w, h, QColor.fromRgb(201, 148, 22))
            else:
                qp.fillRect(1, y, w, h, QColor.fromRgb(148, 148, 148))

        qp.drawText(x, y, w, h, 0x81, item.data)
        
            
