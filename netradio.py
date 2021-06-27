
import Queue
import pscan
import aud
import json
import logging

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
        
        
class NextPrevHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx, parent):
        self.ctx = ctx
        self.parent = parent
    
    def onClick(self, button):
        aud.playback_stop()
        aud.playlist_clear()
        
        if button == BUT_NEXT:
            self.parent.radioIdx += 1
            if self.parent.radioIdx >= len(self.parent.radios):
                self.parent.radioIdx = 0
        else:
            self.parent.radioIdx -= 1
            if self.parent.radioIdx < 0:
                self.parent.radioIdx = len(self.parent.radios) - 1
        
        try:
            aud.playlist_addurl(self.parent.radios[self.parent.radioIdx]["url"])
            aud.playback_playpause()
        except Exception as exc:
            logging.error("Failed to add radio to playlist: %s", exc)
        

class NetradioLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.srcHandler = SrcHandler(context)
        self.playHandler = PlayPauseHandler(context)
        self.stopHandler = StopHandler(context)
        self.nextPrevHandler = NextPrevHandler(context, self)
        self.radioIdx = 0
        
    def open(self):
        if self.isOpen:
            return
            
        self.loadRadios()
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.addHandler(self.playHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.addHandler(self.stopHandler, BUT_STOP)
        self.ctx.buttons.addHandler(self.nextPrevHandler, BUT_NEXT)
        self.ctx.buttons.addHandler(self.nextPrevHandler, BUT_PREVIOUS)
        ui = self.ctx.netradio_ui
        ui.show()
        
        aud.playback_stop()
        aud.playlist_clear()
        try:
            aud.playlist_addurl(self.radios[self.radioIdx]["url"])
            aud.playback_playpause()
        except Exception as exc:
            logging.error("Failed to add radio to playlist: %s", exc)
        
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
        self.ctx.buttons.removeHandler(self.nextPrevHandler, BUT_NEXT)
        self.ctx.buttons.removeHandler(self.nextPrevHandler, BUT_PREVIOUS)
        ui = self.ctx.netradio_ui
        ui.hide()
    
    def loadRadios(self):
        try:
            with open("radios.json") as fp:
                self.radios = json.load(fp)
        except Exception as exc:
            self.radios = [{"name":"Indie Pop Rocks!", "url": "https://somafm.com/indiepop.pls"}]
            logging.error("Failed to read radios list: %s", exc)
        if self.radioIdx >= len(self.radios):
            self.radioIdx = 0
