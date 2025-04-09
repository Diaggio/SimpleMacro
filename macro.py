import tkinter as tk
import pyautogui as macro



class MouseMacro:
    def __init__(self,root):
        self.root = root
        self.root.title("Simple Macro")

        self.recordedEvents = []

        #LEFT rightFrame
        self.rightFrame = tk.Frame(root)
        self.rightFrame.grid(row=0,column=0, sticky="nsew")
        self.rightFrame.columnconfigure(0,weight=1)
        self.rightFrame.rowconfigure(0,weight=1)

        #EVENT LIST
        self.eventListLabel = tk.Label(self.rightFrame,text="Events")
        self.eventListLabel.grid(row=0,column=0)

        self.eventList = tk.Listbox(self.rightFrame)
        self.eventList.grid(row=1,column=0,columnspan=2)

        #UPDATE
        self.update = tk.Button(self.rightFrame,text="Update")
        self.update.grid(row=2,column=0)

        #CLEAR
        self.clear = tk.Button(self.rightFrame,text="Clear",command=self.clearList)
        self.clear.grid(row=2,column=1)

        # RIGHT rightFrame
        self.leftFrame = tk.Frame(root,borderwidth=1,relief="solid")
        self.leftFrame.grid(row=0,column=1, sticky="nsew")
        self.leftFrame.config(highlightbackground="red",highlightthickness=2)


        #RECORD HOTKEY
        self.recordHotkeyLabel = tk.Label(self.leftFrame,text="Set Record Hotkey",bg="white",fg="blue",relief="solid",borderwidth=2)
        self.recordHotkeyLabel.grid(row=0,column=0)

        self.recordHotkey = tk.Button(self.leftFrame,text="test")
        self.recordHotkey.grid(row=1,column=0)

        #STOP HOTKEY

        self.stopHotkeyLabel = tk.Label(self.leftFrame,text="Stop Hotkey")
        self.stopHotkeyLabel.grid(row=0,column=1)

        self.stopHotkey = tk.Button(self.leftFrame,text="test")
        self.stopHotkey.grid(row=1,column=1)

        #RECORD

        """ recordLabel = tk.Label(leftFrame,text="Record",bg="white",fg="blue",relief="solid",borderwidth=2)
        recordLabel.grid(row=2,column=0) """

        self.record = tk.Button(self.leftFrame,text="Start Recording",command=self.recordEvent)
        self.record.grid(row=3,column=0)

        #STOP
        """ stopLabel = tk.Label(leftFrame,text="Stop")
        stopLabel.grid(row=2,column=1) """

        self.stop = tk.Button(self.leftFrame,text="Stop Recording")
        self.stop.grid(row=3,column=1)

        #REPEAT
        self.repeatLabel = tk.Label(self.leftFrame,text="Enter number of macro repetitions")
        self.repeatLabel.grid(row=4, column=0, columnspan=2, pady=(10, 0),sticky="ew")

        self.repeat = tk.Entry(self.leftFrame)
        self.repeat.grid(row=5,column=0)

        #SPEED
        self.speedLabel = tk.Label(self.leftFrame,text="Speed")
        self.speedLabel.grid(row=6,column=0)

        self.speed = tk.OptionMenu(self.leftFrame,"2x","1x")
        self.speed.grid(row=7,column=0)

        #START
        self.start = tk.Button(self.leftFrame,text="Run Macro")
        self.start.grid(row=8,column=0)

    def clearList(self):
        self.eventList.delete(0,tk.END)

    def recordEvent():
        ...




#screenWidth, screenHeight = macro.size()

#macro.displayMousePosition()
root = tk.Tk()
app = MouseMacro(root)
root.mainloop()