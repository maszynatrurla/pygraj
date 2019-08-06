
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

from gui_al import *
import scroll_list
import artist_sc_handler
import album_song_sc_handler

class EsdePanel(QWidget):
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
        
        qp.end()


class EsdeView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = EsdePanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
        self.ctx.artists_view = scroll_list.ScrollableList(self.widget, 3, 3, w / 3 - 6, h - 6, artist_sc_handler.ArtistListHandler())
        self.ctx.songs_view = scroll_list.ScrollableList(self.widget, 6 + w / 3, 3, 2 * w / 3 - 6, h - 6, album_song_sc_handler.AlbumSongListHandler())
        
    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()
