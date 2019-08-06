
from PyQt5.QtGui import QColor, QFont

class ArtistListHandler:
    
    def __init__(self):
        pass
        
    def calculateSize(self, item):
        return (0, 28)
        
    def preparePainter(self, qp):
        qp.setFont(QFont("DejaVu Serif", 14))
        
    def paint(self, item, qp, x, y, w, h, is_selected):
        if is_selected:
            qp.fillRect(1, y, w, h, QColor.fromRgb(201, 148, 22))

        qp.drawText(x, y, w, h, 0x81, item)
        
            
