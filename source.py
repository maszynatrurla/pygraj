
import pscan
import aud
from hardconf import *
import ui_source
import Queue


class UpHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("move_up")
        
class DownHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("move_down")

class EnterHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        self.ctx.event_queue.put("enter")

class StopHandler(pscan.CzypiskHandler):
    
    def __init__(self, ctx):
        self.ctx = ctx
    
    def onPress(self, button):
        aud.playback_stop()



class SourceLayer:
    
    def __init__(self, context):
        self.ctx = context
        self.isOpen = False
        self.openDelayed = False
        
        self.upHandler = UpHandler(context)
        self.downHandler = DownHandler(context)
        self.enterHandler = EnterHandler(context)
        self.stopHandler = StopHandler(context)
        
    def open(self):
        if self.isOpen:
            return
        
        self.ctx.buttons.addHandler(self.upHandler, BUT_UP)
        self.ctx.buttons.addHandler(self.downHandler, BUT_DOWN)
        self.ctx.buttons.addHandler(self.enterHandler, BUT_ENTER)
        self.ctx.buttons.addHandler(self.stopHandler, BUT_STOP)
        self.openDelayed = True
        self.isOpen = True
        
    def cycle(self):
        ui = self.ctx.source_ui
        if ui is None:
            return
        
        try:
            if self.openDelayed:
                ui.show()
                self.openDelayed = False
            
            msg = self.ctx.event_queue.get(timeout=.5)
            if msg == "move_up":
                ui.move(-1)
            elif msg == "move_down":
                ui.move(1)
            elif msg == "enter":
                pos = ui.getPos()
                if pos is not None:
                    item = SRC_ITEMS[pos]
                    
                    if "TT_SRC_ITEM_LOCAL_STORAGE"  == item:
                        return self.ctx.esde_layer
                    elif "TT_SRC_ITEM_CD"             == item:
                        return self.ctx.cede_layer
                    elif "TT_SRC_ITEM_INTERNET_RADIO" == item:
                        return self.ctx.netradio_layer
                    elif "TT_SRC_ITEM_PODCASTS"       == item:
                        return self.ctx.pod_layer
                    
        except Queue.Empty:
            pass
        
    def close(self):
        self.isOpen = False
        self.openDelayed = False
        
        self.ctx.buttons.removeHandler(self.upHandler, BUT_UP)
        self.ctx.buttons.removeHandler(self.downHandler, BUT_DOWN)
        self.ctx.buttons.removeHandler(self.enterHandler, BUT_ENTER)
        self.ctx.buttons.removeHandler(self.stopHandler, BUT_STOP)
        ui = self.ctx.source_ui
        if ui is not None:
            ui.hide()
