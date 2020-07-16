#!/usr/bin/env python

import sys
import logging
import logging.handlers
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

PID_FILE="/run/user/1000/pygraj.pid"

LOG_LEVEL="INFO"
LOG_FILE="/run/user/1000/pygraj.log"
LOG_MAX_SIZE=2 * 1024 * 1024
LOG_BACKUPS=2

def create_pid_file():
    try:
        with open(PID_FILE, "w") as fp:
            fp.write(str(os.getpid()))
    except IOError:
        print("Unable to create PID file.")
        sys.exit(-2)

def log_init():
    logging.basicConfig()
    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s %(message)s")
    handler = logging.handlers.RotatingFileHandler(LOG_FILE,
                maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUPS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
        
        
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
    create_pid_file()
    log_init()
    
    logging.info("Starting application")
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
    except KeyboardInterrupt:
        logging.info("Stopping by INT signal")
    except:
        logging.error("Uncaught exception in main! Traceback follows")
        logging.error(traceback.format_exc())
    
    end_event.set()
    psc.stop()
        
    for t in threads:
        t.join()
    
    return ret
    

if __name__ == "__main__":
    sys.exit(main())


