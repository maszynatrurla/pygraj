#!/usr/bin/env python

import sys
import logging
import threading
import time
import traceback
import Queue
import os
import subprocess

from PyQt5.QtWidgets import QApplication

import pscan
import window
import source
import cede
import esde
import netradio
import pod
import nowplay

def log_init():
    logging.basicConfig()
    logging.getLogger().setLevel("INFO")
    
        
        
class Context:
    def __init__(self):
        self.buttons = None
        self.window = None
        

def control_thread(end, context):
    context.event_queue = Queue.Queue()
    context.source_layer.open()
    
    current_layer = context.source_layer
    
    while not end.is_set():
        
        next_layer = current_layer.cycle()
        
        if next_layer is not None and next_layer != current_layer:
            current_layer.close()
            next_layer.open()
            current_layer = next_layer
            
        
def create_gui(context):
    gui = window.Gui(context)
    return gui.createMainWindow()


def createLayers(context):
    context.source_layer = source.SourceLayer(context)
    context.source_ui = None
    context.cede_layer = cede.CedeLayer(context)
    context.esde_layer = esde.EsdeLayer(context)
    context.netradio_layer = netradio.NetradioLayer(context)
    context.pod_layer = pod.PodLayer(context)
    context.nowplay_layer = nowplay.NowPlayingLayer(context)
    
def main():
    ret = -1
    context = Context()
    end_event = threading.Event()

    psc = pscan.CzypiskThread()
    context.buttons = psc
    
    createLayers(context)
        
    threads = []
    threads.append(psc)
    threads.append(threading.Thread(target=control_thread, kwargs = {'end' : end_event, 'context' : context}))
    
    for t in threads:
        t.start()
        
    try:
        app = QApplication(sys.argv)
        window = create_gui(context)
        context.window = window
        window.show()
        ret = app.exec_()
    except:
        traceback.print_exc()
    
    end_event.set()
    psc.stop()
        
    for t in threads:
        t.join()
    
    return ret
    

if __name__ == "__main__":
    sys.exit(main())


