
import Queue
import pscan
import aud

from hardconf import *

class SrcHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("source")
        
class PlayPauseHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        aud.playback_playpause()
        self.ctx.event_queue.put("playing-changed")
        
class StopHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onClick(self, button):
        aud.playback_stop()
        self.ctx.event_queue.put("playing-changed")

class NetradioLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.srcHandler = SrcHandler(context)
        self.playHandler = PlayPauseHandler(context)
        self.stopHandler = StopHandler(context)
        
    def open(self):
        if self.isOpen:
            return
        
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.addHandler(self.playHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.addHandler(self.stopHandler, BUT_STOP)
        ui = self.ctx.netradio_ui
        ui.show()
        
        aud.playlist_clear()
        aud.playlist_addurl("https://somafm.com/indiepop.pls")
        
        self.isOpen = True
        
    def cycle(self):
        
        self.ctx.netradio_ui.update(aud.current_song())
        
        try:
            msg = self.ctx.event_queue.get(timeout=.2)
            if msg == "source":
                return self.ctx.source_layer
            elif msg == "playing-changed":
                pass
                
        except Queue.Empty:
            pass
        
    def close(self):
        self.isOpen = False
        self.ctx.buttons.removeHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.removeHandler(self.playHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.removeHandler(self.stopHandler, BUT_STOP)
        ui = self.ctx.netradio_ui
        ui.hide()
    

