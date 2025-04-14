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
        self.mousePosQueue = queue.Queue()
        self.mouseListener = None

        self.mouseQueueThrottle = 0.0
        self.mousePosQueueThrottle = 0.0

        self.lastMousePos = None
        self.mouseDisplaySchedule = False

        self.keyboardListener = None
        self.recording = False

        #MACRO CONTROLS
        self.macroRunning = False
        self.totalRepetitions = 0
        self.currentRepetitions = 0
        self.currentEventIndex = 0
        self.nextPlayback = None

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

        self.mousePosVar = tk.StringVar()
        self.mousePosVar.set("Inactive")
        self.mousePosLabel = tk.Label(self.rightFrame,textvariable=self.mousePosVar)
        self.mousePosLabel.grid(row=8,column=1)


        #STATUS LABEL
        self.statusVar = tk.StringVar()
        self.statusVar.set("Status: Idle")
        self.statusLabel = tk.Label(self.rightFrame,textvariable=self.statusVar)
        self.statusLabel.grid(row=9,column=0)

        self.startListener()
        self.processMouseQueue()
        #self.processMouseDisplayQueue()
        self.lastTime = 0


        self.root.protocol("WM_DELETE_WINDOW", self.closeApp)


    def clearList(self):
        self.eventList.delete(0,tk.END)
        self.recordedEvents = []


    def startListener(self):
        if self.mouseListener is None or not self.mouseListener.is_alive():
            self.mouseListener = mouse.Listener(on_move=self.mouseMove,
                                           on_click=self.mouseClick)
            self.mouseListener.start()
            #self.mouseListener.stop()
            

    def mouseClick(self,x,y,button,pressed):
        if self.recording:
            try:
                self.mouseQueue.put(("click",x,y,button,pressed,time.time()))
            except:
                print(f"error adding {button} click {x},{y}")

    def mouseMove(self,x,y):
        now = time.time()

        self.lastMousePos = (x,y)
        if not self.mouseDisplaySchedule:
            self.mouseDisplaySchedule = True
            self.root.after(100,self.mousePosDisplay)
            
        if self.recording:
            recordInterval = 0.05
            if now - self.mouseQueueThrottle > recordInterval:
                self.mousePosQueueThrottle = now
            try:
                self.mouseQueue.put(("move",x,y,time.time()))
            except Exception as e:
                print(f"Error adding into queue {e}")


    def processMouseQueue(self):
        try:
            while True:
                eventData = self.mouseQueue.get_nowait()
                eventType = eventData[0]
                self.recordedEvents.append(eventData)
                x,y = eventData[1],eventData[2]

                if eventType == "click":
                    button,pressed = eventData[3],eventData[4]
                    if pressed:
                        self.eventList.insert(tk.END,f"click {button} at {x},{y}")

        except queue.Empty:
            pass
        finally:
            self.root.after(100,self.processMouseQueue)


    def processMouseDisplayQueue(self):
        latestPos = None

        try:
            while not self.mousePosQueue.empty():
                latestPos = self.mousePosQueue.get_nowait()

                if latestPos is not None:
                    x,y = latestPos
                    self.mousePosDisplay(x,y)

        except queue.Empty():
            pass
        finally:
            self.root.after(100,self.processMouseDisplayQueue)

    def mousePosDisplay(self):
        if self.lastMousePos:
            x,y = self.lastMousePos
            self.mousePosVar.set(f"pos at {int(x)} and {int(y)}")
        self.mouseDisplaySchedule= False


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

            if self.recordedEvents:
                lastEvent = self.recordedEvents[-1]
                if lastEvent[0] == "click":
                    self.recordedEvents.pop()
                    self.eventList.delete(tk.END)

    def macroController(self):
        
        if not self.macroRunning:
            self.runMacro()
        else:
            self.stopMacro()

    def runMacro(self):
        self.macroRunning = True
        if not self.recordedEvents:
            print("no recorded events")
            self.stopMacro()
            return;
        
        try:
           self.totalRepetitions = int(self.repeat.get())
           self.start.config(text="Stop Macro", fg="red")
        except ValueError:
           print("invalid repetition count")
           self.stopMacro()
           return
        
        if self.totalRepetitions <= 0:
            print("repetitions must be positive")
            self.stopMacro()
            return
        
        self.currentRepetitions = 1
        self.currentEventIndex = 0
        self.statusVar.set(f"Rep:{self.currentRepetitions} / {self.totalRepetitions}")
        self.nextPlayback = self.root.after(10, self.macroLogic)

    def stopMacro(self):
        self.macroRunning = False
        if self.nextPlayback:
            self.root.after_cancel(self.nextPlayback)
            self.nextPlayback = None
        self.start.config(text="Run Macro",fg="black")
        self.statusVar.set("Macro Stopped")
        print("Macro Stopped")

    def macroLogic(self):
        if not self.macroRunning:
            print("macro stopped")
            return
        

        
        if not self.recordedEvents or self.currentEventIndex >= len(self.recordedEvents):
            
            self.currentRepetitions += 1
            if self.currentRepetitions > self.totalRepetitions:
                self.macroFinished()
                return
            
            self.currentEventIndex = 0
            self.statusVar.set(f"Rep:{self.currentRepetitions} / {self.totalRepetitions}")
            
            #the 500 deay here is to set the next iteration of events
            self.nextPlayback = self.root.after(500, self.macroLogic)
            return
        


        try:
            currentEvent = self.recordedEvents[self.currentEventIndex]
            eventType = currentEvent[0]
            timeStamp = currentEvent[-1]
        except IndexError:
            print("tried accessing the wrong index")
            self.currentEventIndex +=1
            self.nextPlayback = self.root.after(10,self.macroLogic)
            return
        
        if eventType == "click":
            _, x, y, button, pressed, _ = currentEvent
            self.mouseControl.position = (x,y)

            if pressed:
                self.mouseControl.press(button)
            else:
                self.mouseControl.release(button)
        elif eventType == "move":
            _, x ,y ,_ = currentEvent
            self.mouseControl.position = (x,y)
        
        delay = 10
        nextIndex = self.currentEventIndex + 1
        if nextIndex < len(self.recordedEvents):
            nextTimeStamp = self.recordedEvents[nextIndex][-1]
            delaySeconds = nextTimeStamp - timeStamp
            delay = max(1,int(delaySeconds * 1000))
            
        
            
        self.currentEventIndex +=1
        
        #the delay here sets time between macro events 
        self.nextPlayback = self.root.after(delay,self.macroLogic)


        
    def macroFinished(self):
        print("macro finished all repetitions")
        self.statusVar.set("macro finished all repetitions")
        self.macroRunning = False
        self.nextPlayback = None
        self.start.config(text="Run Macro",fg="black")

    def closeApp(self):
        if self.mouseListener and self.mouseListener.is_alive():
            self.mouseListener.stop()

        self.root.destroy()



#screenWidth, screenHeight = macro.size()

#macro.displayMousePosition()
root = tk.Tk()

app = MouseMacro(root)
root.mainloop()