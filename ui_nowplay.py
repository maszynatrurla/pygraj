
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen, QImage
from PyQt5.QtCore import QRect

from gui_al import *

import scroll_list
import nowplay_sc_handler

class NowPlayingPanel(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        sw, sh = getScreenSize()
        qp.fillRect(0, 0, sw, sh, QColor.fromRgb(0, 0, 0))
        
        qp.end()
        
class AlbumArtPanel(QLabel):
    def __init__(self, parent, x, y, w, h):
        QWidget.__init__(self, parent)
        self.setGeometry(x, y, w, h)
        self.dims = (w, h)
        self.drawArt = False
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        ww, wh = self.dims
        
        if self.drawArt:
            image = QImage('/var/run/user/1000/pygraj_cover.jpg')
            rect = QRect(0, 0, ww, wh)
            qp.drawImage(rect, image)

        qp.end()
        
    def setArt(self, drawArt):
        self.drawArt = drawArt
        self.update()
        
class PlayStatusView(QWidget):
    def __init__(self, ctx, parent, x, y, w, h):
        QWidget.__init__(self, parent)
        self.ctx = ctx
        self.setGeometry(x, y, w, h)
        self.dims = (w, h)
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        ww, wh = self.dims
        qp.fillRect(0, 0, ww, wh, QColor.fromRgb(0, 0, 0))
        qp.setPen(QPen(QColor.fromRgb(255, 255, 255), 2, 1, 0, 0x80))
        
        if self.ctx.playlist.position > 0 and self.ctx.playlist.position <= len(self.ctx.playlist.tracks):
            track, title, tlen = self.ctx.playlist.tracks [self.ctx.playlist.position - 1]
            qp.drawText(2, 2, ww - 4, wh - 4, 0x84, title)
               
        qp.end()

class NowPlayingView:
    
    def __init__(self, context):
        self.ctx = context
        
    def construct(self, parent):
        self.widget = NowPlayingPanel(parent)
        w, h = getScreenSize()
        self.widget.hide()
        self.widget.setGeometry(0, 0, w, h)
        
        self.ctx.album_art_view = AlbumArtPanel(self.widget, 3, 3, (w - 9) / 2, int((h - 9) * .8))
        self.ctx.playsongs_list_handler = nowplay_sc_handler.NowplayListHandler(self.ctx)
        self.ctx.playsongs_view = scroll_list.ScrollableList(self.widget, (w - 9) / 2 + 3, 3, (w - 9) / 2, int((h - 9) * .8), self.ctx.playsongs_list_handler)
        self.ctx.playsongs_view.setBorder(False)
        self.ctx.playstatus_view = PlayStatusView(self.ctx, self.widget, 3, int(h * 0.8) - 3, w - 6, int((h - 9) * .2))

    def show(self):
        self.widget.show()
        
    def hide(self):
        self.widget.hide()
