from verisium import *
import tkinter as tk
import tkinter.ttk as ttk

class HelloVDBApp(VDBTkInterApp):
    """
    HelloVDBApp
    A sample Python API application.
    Click the added 'hello' button on the waveform for a message.
    """

    VDB_APP_NAME = "Hello VDB App"

    def __init__(self, server, app_dir):
        # Note: we are asking not to use the default app geomery (size of the window), but if you do that you must later
        # specify your own geometry in a similar manner to what we do in HelloVDBTopFrame.__init__
        super().__init__(server, app_dir, use_default_geometry=False)
        self.top_frame = None

    # a simple callback for a button press that displays a message
    def hello_msg(self, _):
        version = self.server.server_info.version
        self.show_info("Hello VDB App", f"Hello running on Verisium Debug version: {version}")

    # start method, called when Verisium Debug starts.
    # code here should not block and should run fast.
    def start(self):
        super().start()
        print(f"HelloVDBApp has started! Install dir: {self.app_dir}")

        self.add_button_to_debugger()

        self.add_menu_bars()

        # create the top frame of the application and pack it into the main tk window
        self.top_frame = HelloVDBTopFrame(self.tk_root(), self)
        self.top_frame.pack(expand=True, fill="both")

    # Example of adding menu bars to the main window (in this App only creates: help -> abort)
    def add_menu_bars(self):
        self.main_menubar = tk.Menu(master=self.tk_root())

        self.help_menu = tk.Menu(master=self.main_menubar, tearoff=False)
        self.help_menu.add_command(label='About', command=self.about)

        self.main_menubar.add_cascade(label='Help', menu=self.help_menu)

        self.tk_root().config(menu=self.main_menubar)

    # open up a dailog with text explaining the goal of this App
    def about(self):
        message = "This App is a basic Hello World App designed to give an example of how we think Apps that use tkinter as their gui framework should be constructed." \
                  "This App adds a button to the waveform tool bar. if you click on it a simple tkinter window will open with a single button. clicking on that button will open" \
                  "a dialog that will say hello and also print the version of Verisium Debbug."
        self.show_info("About HelloVDB App", message)

    # first add a button to Verisiun Debug gui so we can opedn this App (currently it will be in the waveform tool bar)
    def add_button_to_debugger(self):
        waveform = self.server.gui_components(ct.name == "Waveform")[0]
        self.debugger_button = GUIButton(waveform.toolbar, text=" Hello! ")
        self.debugger_button.pack()
        self.debugger_button.bind(EventType.WIDGET_CLICKED, self.show_tk_root)

    # shutdown method, called on app uninstall or shutdown of Python process
    def shutdown(self):
        super().shutdown()
        print ("Hello VDB App shutting down..")
        self.debugger_button.pack_forget()
        self.debugger_button.unbind(EventType.WIDGET_CLICKED, self.show_tk_root)

# an example of a top frame that can be used for contain the different widgets your App requires
# note that it get as params both the tk_root (main window) where it "packs" itself
# and the HelloVDBApp - so it can call methods of the App, get information from it, etc.
class HelloVDBTopFrame(tk.Frame):
    def __init__(self, tk_root: tk.Tk, app: HelloVDBApp):
        super(HelloVDBTopFrame, self).__init__(master=tk_root)
        self.tk_root = tk_root
        self.app = app

        self.tk_root.geometry('300x150+200+200')

        self.say_hello_btn = ttk.Button(master=self, text='Say Hello')
        self.app.tooltip(self.say_hello_btn, "Open a dialog that says hello")

        self.say_hello_btn.pack(pady=50)
        self.say_hello_btn.bind('<Button>', self.app.hello_msg)


