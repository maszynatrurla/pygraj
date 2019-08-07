
import Queue
import pscan

from hardconf import *

class SrcHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onLongPress(self, button):
        self.ctx.event_queue.put("source")
        
    def onClick(self, button):
        self.ctx.event_queue.put("change-view")


class NowPlayingLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.srcHandler = SrcHandler(context)

    def open(self):
        if self.isOpen:
            return
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        ui = self.ctx.nowplay_ui
        ui.show()
        self.isOpen = True
        
    def cycle(self):
        try:
            msg = self.ctx.event_queue.get(timeout=.5)
            if msg == "source":
                return self.ctx.source_layer
            elif msg == "change-view":
                return self.ctx.esde_layer
        except Queue.Empty:
            pass
        
    def close(self):
        self.isOpen = False
        self.ctx.buttons.removeHandler(self.srcHandler, BUT_SOURCE)
        ui = self.ctx.nowplay_ui
        ui.hide()