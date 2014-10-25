import setup

from direct.stdpy import threading, thread
import sys

defaultText = '''
base.cr.currSuitPlanner.showPaths()
'''

defaultText = '''
from panda3d.core import *
n = CollisionNode('n')
n.addSolid(CollisionSphere(0, 0, 0, 1))
np = render.attachNewNode(n)
np.show()
'''

defaultText = '''
from toontown.makeatoon.CustomStatePanel import *
p = CustomStatePanel()
'''

def runInjectorCode_tk():
        global text
        try:
            exec (text.get(1.0, "end"),globals())
        except Exception, e: print e

def openInjector_tk():
    import Tkinter as tk
    from direct.stdpy import thread
    root = tk.Tk()
    root.geometry('600x400')
    root.title('Cogtown (TTH version) Injector')
    root.resizable(False, False)
    global text
    frame = tk.Frame(root)
    text = tk.Text(frame,width=70,height=20)

    text.insert(1.0, defaultText)

    text.pack(side="left")
    tk.Button(root,text="Inject!",command=runInjectorCode_tk).pack()
    scroll = tk.Scrollbar(frame)
    scroll.pack(fill="y",side="right")
    scroll.config(command=text.yview)
    text.config(yscrollcommand=scroll.set)
    frame.pack(fill="y")

    thread.start_new_thread(root.mainloop,())


##################################################
#wx version

def __inject_wx(_):
    code = textbox.GetValue()
    exec (code, globals())

def openInjector_wx():
    import wx
    
    app = wx.App(redirect = False)
        
    frame = wx.Frame(None, title = "TTH Injector", size=(640, 400), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
    panel = wx.Panel(frame)
    button = wx.Button(parent = panel, id = -1, label = "Inject", size = (50, 20), pos = (295, 0))
    global textbox
    textbox = wx.TextCtrl(parent = panel, id = -1, pos = (20, 22), size = (600, 340), style = wx.TE_MULTILINE)
    frame.Bind(wx.EVT_BUTTON, __inject_wx, button)

    frame.Show()
    app.SetTopWindow(frame)
    
    textbox.AppendText(defaultText)
    
    threading.Thread(target = app.MainLoop).start()
    
def handleInstallInjector():
    if not '-inj' in sys.argv:
        return
        
    injType = sys.argv[sys.argv.index('-inj') + 1].lower()

    if injType == "wx":
        openInjector_wx()
        
    elif injType == "tk":
        openInjector_tk()
        
    else:
        raise ValueError('Invalid injector config: %s. Must be "wx" or "tk"!' % injType)
            
handleInstallInjector()

import toontown.toonbase.ToontownStart
