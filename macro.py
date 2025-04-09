import tkinter as tk
from pynput import mouse,keyboard
import queue
import time



class MouseMacro:
    def __init__(self,root):
        self.root = root
        self.root.title("Simple Macro")

        self.recordedEvents = []
        self.mouseControl = mouse.Controller()

        self.mousePosQueue = queue.Queue()
        self.listener = None

        #LEFT rightFrame
        self.leftFrame = tk.Frame(root)
        self.leftFrame.grid(row=0,column=0, sticky="nsew")
        self.leftFrame.columnconfigure(0,weight=1)
        self.leftFrame.rowconfigure(0,weight=1)

        #EVENT LIST
        self.eventListLabel = tk.Label(self.leftFrame,text="Events")
        self.eventListLabel.grid(row=0,column=0)

        self.eventList = tk.Listbox(self.leftFrame)
        self.eventList.grid(row=1,column=0,columnspan=2)

        #UPDATE
        self.update = tk.Button(self.leftFrame,text="Update")
        self.update.grid(row=2,column=0)

        #CLEAR
        self.clear = tk.Button(self.leftFrame,text="Clear",command=self.clearList)
        self.clear.grid(row=2,column=1)

        # RIGHT rightFrame
        self.rightFrame = tk.Frame(root,borderwidth=1,relief="solid")
        self.rightFrame.grid(row=0,column=1, sticky="nsew")
        self.rightFrame.config(highlightbackground="red",highlightthickness=2)


        #RECORD HOTKEY
        self.recordHotkeyLabel = tk.Label(self.rightFrame,text="Set Record Hotkey",bg="white",fg="blue",relief="solid",borderwidth=2)
        self.recordHotkeyLabel.grid(row=0,column=0)

        self.recordHotkey = tk.Button(self.rightFrame,text="test")
        self.recordHotkey.grid(row=1,column=0)

        #STOP HOTKEY

        self.stopHotkeyLabel = tk.Label(self.rightFrame,text="Stop Hotkey")
        self.stopHotkeyLabel.grid(row=0,column=1)

        self.stopHotkey = tk.Button(self.rightFrame,text="test")
        self.stopHotkey.grid(row=1,column=1)

        #RECORD

        """ recordLabel = tk.Label(leftFrame,text="Record",bg="white",fg="blue",relief="solid",borderwidth=2)
        recordLabel.grid(row=2,column=0) """

        self.record = tk.Button(self.rightFrame,text="Start Recording",command=self.recordEvent)
        self.record.grid(row=3,column=0)

        #STOP
        """ stopLabel = tk.Label(leftFrame,text="Stop")
        stopLabel.grid(row=2,column=1) """

        self.stop = tk.Button(self.rightFrame,text="Stop Recording")
        self.stop.grid(row=3,column=1)

        #REPEAT
        self.repeatLabel = tk.Label(self.rightFrame,text="Enter number of macro repetitions")
        self.repeatLabel.grid(row=4, column=0, columnspan=2, pady=(10, 0),sticky="ew")

        self.repeat = tk.Entry(self.rightFrame)
        self.repeat.grid(row=5,column=0)

        #SPEED
        self.speedLabel = tk.Label(self.rightFrame,text="Speed")
        self.speedLabel.grid(row=6,column=0)

        self.speed = tk.OptionMenu(self.rightFrame,"2x","1x")
        self.speed.grid(row=7,column=0)

        #START
        self.start = tk.Button(self.rightFrame,text="Run Macro")
        self.start.grid(row=8,column=0)

        self.test = tk.Label(self.rightFrame,text="test label")
        self.test.grid(row=8,column=1)

        self.startListener()
        self.processMouseQueue()
        self.lastTime = 0


        self.root.protocol("WM_DELETE_WINDOW", self.closeApp)

    def clearList(self):
        self.eventList.delete(0,tk.END)


    def startListener(self):
        if self.listener is None or not self.listener.is_alive():
            self.listener = mouse.Listener(on_move=self.mouseMove)
            self.listener.start()
            

    def mouseMove(self,x,y):
        try:
            self.mousePosQueue.put((x,y))
        except Exception as e:
            print(f"Error adding into queue {e}")

    def processMouseQueue(self):
        try:
            while True:
                x,y = self.mousePosQueue.get_nowait()
                self.testPos(x,y)
        except queue.Empty:
            pass
        finally:
            self.root.after(100,self.processMouseQueue)

    def testPos(self,x,y):
        self.test.config(text=f"pos at {x} and {y}")

    def recordEvent():
        ...

    def closeApp(self):
        if self.listener and self.listener.is_alive():
            self.listener.stop()

        self.root.destroy()



#screenWidth, screenHeight = macro.size()

#macro.displayMousePosition()
root = tk.Tk()
app = MouseMacro(root)
root.mainloop()