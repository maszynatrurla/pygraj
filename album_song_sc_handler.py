
from PyQt5.QtGui import QColor, QFont

def sort_song(songx, songy):
    try:
        return int(songx.props["track"]) - int(songy.props["track"])
    except:
        return 0

def create_content(artist):
    items = []
    album_dir = artist.get("albums", {})
    albums = [name for name in album_dir.keys()]
    albums.sort()
    for name in albums:
        items.append((0, name))
        songs = [song for song in album_dir[name].get("songs", ())]
        songs.sort(sort_song)
        
        for song in songs:
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

    