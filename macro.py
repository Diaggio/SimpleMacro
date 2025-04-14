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

        self.mouseQueue = queue.Queue()
        self.mouseListener = None

        self.keyboardListener = None

        self.recording = False
        self.macroRunning = False

        #LEFT Frame
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

        # RIGHT Frame
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

        self.record = tk.Button(self.rightFrame,text="Start Recording",command=self.recordingStatus)
        self.record.grid(row=3,column=0, columnspan=2)


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
        self.start = tk.Button(self.rightFrame,text="Run Macro", command=self.macroController)
        self.start.grid(row=8,column=0)

        self.mousePosLabel = tk.Label(self.rightFrame,text="test label")
        self.mousePosLabel.grid(row=8,column=1)

        self.startListener()
        self.processMouseQueue()
        self.lastTime = 0


        self.root.protocol("WM_DELETE_WINDOW", self.closeApp)


    def clearList(self):
        self.eventList.delete(0,tk.END)
        self.recordedEvents = []


    def startListener(self):
        if self.mouseListener is None or not self.mouseListener.is_alive():
            self.listener = mouse.Listener(on_move=self.mouseMove,
                                           on_click=self.mouseClick)
            self.listener.start()
            

    def mouseClick(self,x,y,button,pressed):
        if self.recording and pressed:
            try:
                self.mouseQueue.put(("click",x,y,button,pressed))
            except:
                print(f"error adding {button} click {x},{y}")

    def mouseMove(self,x,y):
        try:
            self.mouseQueue.put(("move",x,y))
        except Exception as e:
            print(f"Error adding into queue {e}")

    def processMouseQueue(self):
        try:
            while True:
                eventData = self.mouseQueue.get_nowait()
                eventType = eventData[0]
                x,y = eventData[1],eventData[2]

                if eventType == "move":
                    self.mousePosDisplay(x,y)

                elif eventType == "click":
                    button,pressed = eventData[3],eventData[4]
                    if pressed:
                        self.recordedEvents.append(eventData)
                        self.eventList.insert(tk.END,f"click {button} at {x},{y}")

        except queue.Empty:
            pass
        finally:
            self.root.after(100,self.processMouseQueue)

    def mousePosDisplay(self,x,y):
        self.mousePosLabel.config(text=f"pos at {x} and {y}")


    def recordingStatus(self):
        if not self.recording:
            self.startRecording()
        else:
            self.stopRecording()

    def startRecording(self):
        if not self.recording:
            print("recording started")
            self.recording = True
            self.clearList()
            self.record.config(text="Stop recording",fg="red")
            

    def stopRecording(self):
        if self.recording:
            print("recording stopped")
            self.recording = False
            self.record.config(text="Start recording",fg="black")

    def macroController(self):
        
        if not self.macroRunning:

            self.start.config(text="Stop Macro", fg="red")
            self.runMacro()
        else:
            self.start.config(text="Run Macro", fg="black")
            self.stopMacro()

    def runMacro(self):
        
        try:
           repetitions = int(self.repeat.get())
           eventType, x, y, button, _ = self.recordedEvents
           while repetitions > 0: 
            for i in len(self.recordedEvents):
                if eventType == "click":
                    self.mouseControl.click(button,x,y)

            repetitions -= 1


        except:
            print("error processing recorded events") 


    def closeApp(self):
        if self.listener and self.listener.is_alive():
            self.listener.stop()

        self.root.destroy()



#screenWidth, screenHeight = macro.size()

#macro.displayMousePosition()
root = tk.Tk()

app = MouseMacro(root)
root.mainloop()