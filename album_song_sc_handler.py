
from PyQt5.QtGui import QColor, QFont

def create_content(artist):
    items = []
    for name, album in artist.get("albums", {}).iteritems():
        items.append((0, name))
        for song in album.get("songs", ()):
            items.append((1, song))
        
    return items

class AlbumSongListHandler:
    
    def __init__(self):
        pass
        
    def calculateSize(self, item):
        return (0, 28)
        
    def preparePainter(self, qp):
        qp.setFont(QFont("DejaVu Serif", 14))
        
    def paint(self, item, qp, x, y, w, h, is_selected):
        if is_selected:
            qp.fillRect(1, y, w, h, QColor.fromRgb(201, 148, 22))
            
        tpe, obj = item
        
        if 0 == tpe:
            qp.drawText(x, y, w, h, 0x81, obj)
        else:
            text = u"    " + str(obj.props["track"]) + u" " + obj.props["song"]
            qp.drawText(x, y, w, h, 0x81, text)

    