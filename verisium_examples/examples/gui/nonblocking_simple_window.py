# Copyright 2023 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This source code ("Software") is part of the Verisium Debug API package, the proprietary
# and confidential information of Cadence or its licensors, and supplied
# subject to, and may be used only by Cadence's customer in accordance with a
# previously executed agreement between Cadence and that customer ("Customer").
#
# Permission is hereby granted to such Customer to use and make copies of this
# Software to connect and interact with a Cadence Verisium Debug product from
# Customer's Python program, subject to the following conditions:
#
# - Customer may not distribute, sell, or otherwise modify the Verisium Debug API package.
#
# - All copyright notices in this Software must be maintained on all included
#   Python libraries and packages used by Customer.

import tkinter as tk
import threading
import time
from tkinter import *
from verisium import *

# an example tkinter application that pops up a stay-on-top window when a user hits a
# button that is on the waveform toolbar.
# run verisium debug with -input tk_button_launch.py
class Application(tk.Frame):
    server = None
    root = None
    def __init__(self, server=None, root=None):

        self.root=root
        self.server = server
        super().__init__(self.root)

        # get a handle to the first waveform window (probably only one)
        wave = server.gui_components(ct.name == "Waveform")[0]

        # add buttons. give each a label, and an action string which will be used
        # as a function to call in the button event callback.
        wave.add_button(label="TK Test", action="show_gui")

        # add callbacks for when someone presses the GUI button we added above,
        # and also one for if time is changed.
        server.add_callback(EventType.GUI_BUTTON, self.gui_btn_callback)
        server.add_callback(EventType.CDL_CHANGE, self.time_callback)

        # force the window to remain above others
        self.root.attributes("-topmost", True)

        # configuration of the dialog popup outer Frame
        self.root.geometry("300x100")
        self.root.title("Simple TK Window")
        self.root.configure(background=guicolor.WHITE.name)
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws / 2) - (300)
        y = (hs / 2) - (100)
        self.root.geometry('+%d+%d' % (x, y))

        self.pack(fill=tk.BOTH)
        self.cur_time = tk.StringVar()
        self.create_widgets()

        # allow callers from outside the thread to trigger window toggles by
        # writing to this object's hidden variable.
        self.hidden = BooleanVar(value=False)
        self.hidden.trace_add('write',self.toggle_window)

        # we override the 'x' window close button to just hide the window
        self.master.protocol("WM_DELETE_WINDOW", self.set_hidden)

    # constructs a simple GUI with multiple frames
    def create_widgets(self):
        self.time_label = tk.Label(self, text="CURRENT DEBUG TIME = ?", fg="white", bg="#457ABB")
        self.time_label.pack(side=tk.LEFT, padx = 15, pady = 15)


    # directly set window hidden (only used for window [x] )
    def set_hidden(self):
        self.hidden.set(True)

    # set the window to hidden/visible based on self.hidden state
    def toggle_window(self,var,index,mode):
        if self.hidden.get() is True:
            self.root.withdraw()
        else:
            self.root.update()
            self.root.deiconify()

    # callback when someone changes time in Verisium Debug.
    def time_callback(self, se:ServerEvent):
        self.time_label.config(text="CURRENT DEBUG TIME = "+str(se.time))

    # callback for the button gui_button event whos details are 'show_gui'
    # causes the application window to be visible or hidden.
    def show_gui(self, ev):
        self.hidden.set(not self.hidden.get())

    # callback when someone presses the TK Test button on the waveform
    def gui_btn_callback(self, ev):
        # call the function specified in the 'action' param of the button add by name
        # alternatively, you could write functional code that looks at the button name
        # eg:  if ev.name == "TK Tester"
        # instead of this reflective function call based on the action string.
        getattr(self,ev.details)(ev)

#=======================================================================
# GUI thread that runs separately from main.
# Launch GUI windows here to avoid blocking the embedded console or event threads.
class GUIThread(threading.Thread):
    def __init__(self, server=None):
        threading.Thread.__init__(self, daemon=True)
        self.thread_name="TKinter Window"
        self.thread_ID = 1111
        self.server = server
        self.app = None

    # When the GUI thread is started, an application is launched for the popup.
    # (If you have multiple windows that need to run simultaneously, they should have
    # their own threads)
    def run(self):
        self.root = tk.Tk()
        self.app = Application(server=self.server, root=self.root)
        self.app.hidden.set(True)
        self.app.mainloop()

#=======================================================================

# get the Server. when running with interactive Verisium Debug, this is self, when running via a remote script,
# get it from the design
server = None


# For debug only.  you can run the script in Pycharm etc for debugging and launch Verisium Debug in GUI Mode.
if 'self' not in globals():
   server = VerisiumDebugServer(VerisiumDebugArgs(
            is_gui=True,
            is_launch_needed=True,
            db='<path to your DB>'
        ))
# when the script is used normally, just supply it to -input or using VERISIUMDEBUGPYTHONSTARTUP env var.
# in this scenario the server is the embedded python and is equivalent to 'self'
else:
    server=self

# create a thread to run GUI stuff on that does not block the console etc.
if __name__ == '__main__':
    gui_thread = GUIThread(server)
    gui_thread.setDaemon(True)
    gui_thread.start()

    # keep script from ending and closing Verisium Debug if we are running non-interactively (eg debugging)
    if 'self' not in globals():
        while(True):
            time.sleep(1)









