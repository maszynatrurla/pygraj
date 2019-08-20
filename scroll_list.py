
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen


class ScrollableList(QWidget):

    def __init__(self, parent, posx, posy, width, height, contentHandler):
        QWidget.__init__(self, parent)
        self.setGeometry(posx, posy, width, height)
        self.dims = (width, height)
        self.content = []
        self.scroll_window = (0,0)
        self.selected = []
        self.focused = False
        self.handler = contentHandler
        self.hasBorder = True
        
    def setBorder(self, hasBorder):
        self.hasBorder = hasBorder
        
    def calculateScrollWin(self):
        if not self.content:
            self.scroll_window = (0,0)
        elif self.scroll_window[0] >= len(self.content):
            hsum = 0
            items = 0
            start = 0
            for idx in xrange(len(self.content) - 1, -1, -1):
                hsum += self.handler.calculateSize(self.content[idx])[1]
                if hsum > self.dims[1]:
                    break
                start = idx
                items += 1
            self.scroll_window = (start, items)
        else:
            hsum = 0
            items = 0
            start = 0
            for item in self.content:
                hsum += self.handler.calculateSize(item)[1]
                if hsum > self.dims[1]:
                    break
                items += 1
            self.scroll_window = (start, items)
        
    def focus(self):
        if not self.selected and self.content:
            self.selected.append(self.scroll_window[0])
        if not self.focused:
            self.focused = True
            self.handler.focus()
            self.update()
        
    def unfocus(self):
        if self.focused:
            self.focused = False
            self.handler.unfocus()
            self.update()
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        
        ww, wh = self.dims
        qp.fillRect(0, 0, ww, wh, QColor.fromRgb(0, 0, 0))
        qp.setPen(QPen(QColor.fromRgb(255, 255, 255), 2, 1, 0, 0x80))
        if self.hasBorder:
            qp.drawRect(1, 1, ww - 2 , wh - 2)
        
        if self.content:
            self.paintScroll(qp)
            
        xoff = 3
        xlen = ww - 8
        yoff = 3
        
        self.handler.preparePainter(qp)
        
        for idx in xrange(self.scroll_window[0], self.scroll_window[0] + self.scroll_window[1]):
            if idx >= len(self.content):
                break
            item = self.content[idx]
            item_preffered_size = self.handler.calculateSize(item)
            
            if idx in self.selected:
                self.handler.paint(item, qp, xoff, yoff, xlen, item_preffered_size[1], True)
            else:
                self.handler.paint(item, qp, xoff, yoff, xlen, item_preffered_size[1], False)
                
            yoff += item_preffered_size[1]
        
        qp.end()
        
    def paintScroll(self, qp):
        ww, wh = self.dims
        max_scroll_len = wh - 6
        min_scroll_len = 6
        scroll_len = int(max_scroll_len * (float(self.scroll_window[1]) / len(self.content)))
        
        if scroll_len < min_scroll_len:
            scroll_len = min_scroll_len

        scroll_start = int(max_scroll_len * (float(self.scroll_window[0]) / len(self.content)))
        if scroll_start + scroll_len > max_scroll_len:
            scroll_start = max_scroll_len - scroll_len
        
        if scroll_len < max_scroll_len:
            ww, wh = self.dims
            qp.drawLine(ww - 5, 3 + scroll_start, ww - 5, 3 + scroll_start + scroll_len)
        
    def setContent(self, content):
        self.selected = []
        self.content = []
        self.content.extend(content)
        self.calculateScrollWin()
        self.update()
        
    def getContent(self):
        return self.content
        
    def removeAll(self):
        self.selected = []
        self.content = []
        self.calculateScrollWin()
        self.update()
        
    def addContentItem(self, item):
        self.selected = []
        self.content.append(item)
        self.calculateScrollWin()
        self.update()
        
    def removeContentItem(self, item):
        self.selected = []
        self.content.remove(item)
        self.calculateScrollWin()
        self.update()
        
    def removeContentIndex(self, index):
        self.selected = []
        del self.content[index]
        self.calculateScrollWin()
        self.update()
        
    def select(self, index):
        if index not in self.selected:
            self.selected.append(index)
            self.update()

    def moveSelection(self, move, follow = True, wrap = False):
        if not self.content:
            return
        if not self.selected:
            self.selected.append(self.scroll_window[0])
            
        self.selected[-1] += move
        if self.selected[-1] < 0:
            if wrap:
                self.selected[-1] = len(self.content) - 1
            else:
                self.selected[-1] = 0
        elif self.selected[-1] >= len(self.content):
            if wrap:
                self.selected[-1] = 0
            else:
                self.selected[-1] = len(self.content) - 1
                
        if follow:
            self.scrollToReveal(self.selected[-1])
                
        self.update()
                
    def scrollToReveal(self, position_idx):
        if self.content and position_idx >= 0 and position_idx < len(self.content):
            if self.scroll_window[0] > position_idx:
                hsum = 0
                items = 0
                for idx in xrange(position_idx, len(self.content)):
                    hsum += self.handler.calculateSize(self.content[idx])[1]
                    if hsum > self.dims[1]:
                        break
                    items += 1
                self.scroll_window = (self.selected[-1], items)
                
            elif position_idx >= self.scroll_window[0] + self.scroll_window[1]:
                hsum = 0
                items = 0
                start = 0
                for idx in xrange(position_idx, -1, -1):
                    hsum += self.handler.calculateSize(self.content[idx])[1]
                    if hsum > self.dims[1]:
                        break
                    start = idx
                    items += 1
                self.scroll_window = (start, items)
        
    def deselect(self, index):
        if index in self.selected:
            self.selected.remove(index)
            self.update()
        
    def selectAll(self):
        self.selected = [idx for idx in xrange(len(self.content))]
        self.update()
        
    def deselectAll(self):
        self.selected = []
        self.update()
        
    def getSelection(self):
        if self.selected:
            return self.content[self.selected[-1]]
        else:
            return None
            
    def getSelectionIndex(self):
        if self.selected:
            return self.selected[-1]
        else:
            return -1
    
