
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import QPoint, QRect

import ui_source
import ui_pod
import ui_esde
import ui_netradio
import ui_cede


class MyDimensions:
    WIDTH = 800
    HEIGHT = 480

class Window(QWidget):
    """
    Application window.
    """

    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        #self.playlist = None
        #self.position = 0
        self.create()

    def create(self):
        """
        Create contents.
        """
        self.resize(MyDimensions.WIDTH, MyDimensions.HEIGHT)
        self.setWindowTitle("pygraj")

def createLayers(window, context):
    context.source_ui = ui_source.SourceView(context)
    context.source_ui.construct(window)
    context.esde_ui = ui_esde.EsdeView(context)
    context.esde_ui.construct(window)
    context.cede_ui = ui_cede.CedeView(context)
    context.cede_ui.construct(window)
    context.netradio_ui = ui_netradio.NetradioView(context)
    context.netradio_ui.construct(window)
    context.pod_ui = ui_pod.PodView(context)
    context.pod_ui.construct(window)
    

class Gui:
    
    def __init__(self, context):
        self.context = context
        
        
    def createMainWindow(self):
        window =  Window(self)
        createLayers(window, self.context)
        return window


