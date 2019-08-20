

import Queue
import pscan
import pickle

from hardconf import *

import album_song_sc_handler
import aud

from inventory import *

class SrcHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onLongPress(self, button):
        self.ctx.event_queue.put("source")
        
    def onClick(self, button):
        self.ctx.event_queue.put("change-view")
        
class EnterHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("enter")
        
class StopHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onClick(self, button):
        aud.playback_stop()
        self.ctx.event_queue.put("playing-changed")
        
class UpHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("u1")
        
    def onLongPress(self, button):
        self.ctx.event_queue.put("u8")
        
        
class DownHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("d1")
        
    def onLongPress(self, button):
        self.ctx.event_queue.put("d8")
        
class LeftHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("<")
        
class RightHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put(">")
        
class EqueueHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        aud.playback_playpause()
        self.ctx.event_queue.put("equeue")

class EsdeLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.srcHandler       = SrcHandler(context)
        self.enterHandler     = EnterHandler(context)
        self.stopHandler      = StopHandler(context)
        self.upHandler        = UpHandler(context)
        self.downHandler      = DownHandler(context)
        self.leftHandler      = LeftHandler(context)
        self.rightHandler     = RightHandler(context)
        self.equeueHandler    = EqueueHandler(context)
        self.do_not_refresh_lists = False
        
        with open("music.library") as fp:
            self.library = pickle.load(fp)
        
    def open(self):
        if self.isOpen:
            return
        
        self.ctx.buttons.addHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.addHandler(self.enterHandler, BUT_ENTER)
        self.ctx.buttons.addHandler(self.stopHandler     , BUT_STOP)
        self.ctx.buttons.addHandler(self.upHandler       , BUT_UP)
        self.ctx.buttons.addHandler(self.downHandler     , BUT_DOWN)
        self.ctx.buttons.addHandler(self.leftHandler     , BUT_LEFT)
        self.ctx.buttons.addHandler(self.rightHandler    , BUT_RIGHT)
        self.ctx.buttons.addHandler(self.equeueHandler   , BUT_QUEUE)
        
        if not self.do_not_refresh_lists:
            artists = [artist for artist in self.library.keys()]
            artists.sort()
            self.ctx.artists_view.setContent(artists)
            self.ctx.songs_view.unfocus()
            self.ctx.artists_view.focus()
            self.focused = self.ctx.artists_view
            self.unfocused = self.ctx.songs_view
            self.move_list_selection()
            self.do_not_refresh_lists = False
        ui = self.ctx.esde_ui
        ui.show()
        
        
        self.isOpen = True
        
    def move_list_selection(self):
        if self.focused == self.ctx.artists_view:
            selected_artist = self.focused.getSelection()
            if selected_artist is None:
                return
            content = album_song_sc_handler.create_content(self.library[selected_artist])
            self.ctx.songs_view.setContent(content)
            
    def play_song(self):
        selection = self.ctx.songs_view.getSelection()
        if selection is None:
            return
        
        if selection[0] == 0:
            self.play_album()
        else:
            content = self.ctx.songs_view.getContent()
            
            aud.playback_stop()            
            aud.playlist_clear()
            
            for idx in xrange(self.ctx.songs_view.getSelectionIndex(), len(content)):
                tpe, obj = content[idx]
                if tpe == 1:
                    aud.playlist_addurl(obj[0])
            
            aud.playback_playpause()
            
    def play_album(self):
            content = self.ctx.songs_view.getContent()
            
            aud.playback_stop()            
            aud.playlist_clear()
            
            for idx in xrange(self.ctx.songs_view.getSelectionIndex() + 1, len(content)):
                tpe, obj = content[idx]
                if tpe == 1:
                    aud.playlist_addurl(obj[0])
                else:
                    break
            
            aud.playback_playpause()
        
    def play_artist(self):
        artist_content = self.ctx.songs_view.getContent()
        if not artist_content:
            return
            
        aud.playback_stop()
        aud.playlist_clear()
        
        for tpe, obj in artist_content:
            if tpe == 1:
                aud.playlist_addurl(obj[0])
        
        aud.playback_playpause()
        
    def cycle(self):
        try:
            msg = self.ctx.event_queue.get(timeout=.5)
            if msg == "source":
                return self.ctx.source_layer
            elif msg == "change-view":
                self.do_not_refresh_lists = True
                return self.ctx.nowplay_layer
            elif msg == ">":
                self.ctx.artists_view.unfocus()
                self.ctx.songs_view.focus()
                self.focused = self.ctx.songs_view
            elif msg == "<":
                self.ctx.songs_view.unfocus()
                self.ctx.artists_view.focus()
                self.focused = self.ctx.artists_view
            elif msg == "u1":
                self.focused.moveSelection(-1, follow = True, wrap = True)
                self.move_list_selection()
            elif msg == "d1":
                self.focused.moveSelection( 1, follow = True, wrap = True)
                self.move_list_selection()
            elif msg == "u8":
                self.focused.moveSelection(-8, follow = True, wrap = False)
                self.move_list_selection()
            elif msg == "d8":
                self.focused.moveSelection( 8, follow = True, wrap = False)
                self.move_list_selection()
            elif msg == "enter":
                if self.focused == self.ctx.songs_view:
                    self.play_song()
                else:
                    self.play_artist()
        except Queue.Empty:
            pass
        
    def close(self):
        self.isOpen = False
        self.ctx.buttons.removeHandler(self.srcHandler, BUT_SOURCE)
        self.ctx.buttons.removeHandler(self.enterHandler, BUT_ENTER)
        self.ctx.buttons.removeHandler(self.stopHandler     , BUT_STOP)
        self.ctx.buttons.removeHandler(self.upHandler       , BUT_UP)
        self.ctx.buttons.removeHandler(self.downHandler     , BUT_DOWN)
        self.ctx.buttons.removeHandler(self.leftHandler     , BUT_LEFT)
        self.ctx.buttons.removeHandler(self.rightHandler    , BUT_RIGHT)
        self.ctx.buttons.removeHandler(self.equeueHandler   , BUT_QUEUE)
        ui = self.ctx.esde_ui
        ui.hide()
    

