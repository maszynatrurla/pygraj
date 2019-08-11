
import Queue
import pscan

from hardconf import *

import aud
import playlist

class SrcHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onLongPress(self, button):
        self.ctx.event_queue.put("source")
        
    def onClick(self, button):
        self.ctx.event_queue.put("change-view")
        
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
        
class EqueueHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        aud.playback_playpause()
        self.ctx.event_queue.put("equeue")

class NowPlayingLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.srcHandler = SrcHandler(context)
        self.playpauseHandler = PlayPauseHandler(context)
        self.nextHandler = NextHandler(context)
        self.previousHandler = PreviousHandler(context)
        self.stopHandler = StopHandler(context)
        self.equeueHandler = EqueueHandler(context)

    def open(self):
        self.raw_playlist = ""
        
        if self.isOpen:
            return
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.addHandler(self.playpauseHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.addHandler(self.nextHandler, BUT_NEXT)
        self.ctx.buttons.addHandler(self.previousHandler, BUT_PREVIOUS)
        self.ctx.buttons.addHandler(self.stopHandler, BUT_STOP)
        self.ctx.buttons.addHandler(self.equeueHandler, BUT_QUEUE)
        
        self.ctx.playlist = playlist.Playlist(self.ctx)
        
        ui = self.ctx.nowplay_ui
        ui.show()
        self.isOpen = True
        
    def updatePlaylist(self):
        out = aud.playlist_display()
        if self.raw_playlist != out:
            self.raw_playlist = out
            self.ctx.playlist.fromText(out)
            self.ctx.playsongs_view.setContent(self.ctx.playlist.tracks)
            self.ctx.playstatus_view.update()
            self.updatePlayback()
            
    def updatePlayback(self):
        changes = False
        position = aud.playlist_position()
        if position != self.ctx.playlist.position:
            self.ctx.playlist.position = position
            changes = True
        
        is_playing = aud.playback_playing()
        if not is_playing and self.ctx.playlist.position >= 0:
            self.ctx.playlist.position = -1
            changes = True
            
        if changes:
            self.ctx.playsongs_view.update()
            self.ctx.playstatus_view.update()
        
        return is_playing
        
    def cycle(self):
        try:
            self.updatePlaylist()
            self.updatePlayback()
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
        self.ctx.buttons.removeHandler(self.playpauseHandler, BUT_PLAYPAUSE)
        self.ctx.buttons.removeHandler(self.nextHandler, BUT_NEXT)
        self.ctx.buttons.removeHandler(self.previousHandler, BUT_PREVIOUS)
        self.ctx.buttons.removeHandler(self.stopHandler, BUT_STOP)
        self.ctx.buttons.removeHandler(self.equeueHandler, BUT_QUEUE)
        ui = self.ctx.nowplay_ui
        ui.hide()