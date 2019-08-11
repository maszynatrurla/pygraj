from PyQt5.QtGui import QColor, QFont

class NowplayListHandler:
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.focused = False
        self.paintedItemIdx = 0
        
    def calculateSize(self, item):
        return (0, 28)
        
    def preparePainter(self, qp):
        self.paintedItemIdx = 0
        qp.setFont(QFont("DejaVu Serif", 14))
        
    def focus(self):
        self.focused = True
        
    def unfocus(self):
        self.focused = False
        
    def paint(self, item, qp, x, y, w, h, is_selected):
        self.paintedItemIdx += 1
        
        if is_selected:
            if self.focused:
                qp.fillRect(1, y, w, h, QColor.fromRgb(201, 148, 22))
            else:
                qp.fillRect(1, y, w, h, QColor.fromRgb(148, 148, 148))
            
        if self.paintedItemIdx == self.ctx.playlist.position:
            qp.setFont(QFont("DejaVu Serif", 14, 75))
        else:
            qp.setFont(QFont("DejaVu Serif", 14, 50))
            
        track, title, tlen = item
            
        qp.drawText(x, y, w, h, 0x81, title)
        