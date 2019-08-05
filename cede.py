
import Queue

import pscan
import aud
import playlist

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
        
class NextHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onClick(self, button):
        aud.playlist_advance()
        self.ctx.event_queue.put("position-changed")
        
class PreviousHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onClick(self, button):
        aud.playlist_reverse()
        self.ctx.event_queue.put("position-changed")
        
class StopHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onClick(self, button):
        aud.playback_stop()
        self.ctx.event_queue.put("playing-changed")
        

class CedeLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        
        self.srcHandler = SrcHandler(context)
        self.playHandler = PlayPauseHandler(context)
        self.nextHandler = NextHandler(context)
        self.prevHandler = PreviousHandler(context)
        self.stopHandler = StopHandler(context)
        
    def open(self):
        if self.isOpen:
            return
        
        self.ctx.playlist = playlist.Playlist(self.ctx)
        self.playlistSM = playlist.PlaylistSM(self.ctx)
        self.playbackSM = playlist.PlaybackSM(self.ctx)
        self.playlistSM.poke()
        
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.addHandler(self.playHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.addHandler(self.nextHandler, BUT_NEXT)
        self.ctx.buttons.addHandler(self.prevHandler, BUT_PREVIOUS)
        self.ctx.buttons.addHandler(self.stopHandler, BUT_STOP)
        ui = self.ctx.cede_ui
        ui.show()
        
        aud.playlist_clear()
        aud.playlist_addurl("cdda://")
        
        self.isOpen = True
        
    def cycle(self):
        try:
            msg = self.ctx.event_queue.get(timeout=.2)
            if msg == "source":
                return self.ctx.source_layer
            elif msg == "playing-changed":
                self.playbackSM.poke()
            elif msg == "position-changed":
                self.playbackSM.poke()
                self.playlistSM.updatePlaylist()
        except Queue.Empty:
            pass
            
        self.playlistSM.cycle()
        self.playbackSM.cycle()
        
    def close(self):
        self.isOpen = False
        self.ctx.buttons.removeHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.removeHandler(self.playHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.removeHandler(self.nextHandler, BUT_NEXT)
        self.ctx.buttons.removeHandler(self.prevHandler, BUT_PREVIOUS)
        self.ctx.buttons.removeHandler(self.stopHandler, BUT_STOP)
        ui = self.ctx.cede_ui
        ui.hide()
    

