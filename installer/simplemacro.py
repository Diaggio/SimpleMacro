import tkinter as tk
from pynput import mouse,keyboard
import queue
import time



class MouseMacro:
    def __init__(self,root):
        self.root = root
        self.root.title("Simple Macro")

        self.recordedEvents = []

        #MOUSE CONTROLS AND PARAMETERS
        self.mouseControl = mouse.Controller()
        self.mouseQueue = queue.Queue()
        self.mousePosQueue = queue.Queue()
        self.mouseListener = None
        self.mouseQueueThrottle = 0.0 
        #self.mousePosQueueThrottle = 0.0 #utilized for displaying mouse position on GUI - lagging on mac
        self.lastMousePos = None
        self.mouseDisplaySchedule = False


        #KEYBOARD CONTROLS AND PARAMETERS
        self.keyboardControl = keyboard.Controller()
        self.keyboardListener = None
        self.recordGlobalHotkey = '<ctrl>+a'
        self.recordGlobalHotkeyListener = keyboard.GlobalHotKeys({
            self.recordGlobalHotkey: self.recordingStatus
        })
        self.isSettingRecordHotKey = False
        self.keyList = []
        self.keyHotKeyList = []

        #MAIN MACRO CONTROLS
        self.isRecording = False
        self.macroRunning = False
        self.totalRepetitions = 0
        self.currentRepetitions = 0
        self.currentEventIndex = 0
        self.nextPlayback = None

        #GUI SETUP
        self.createFrames()
        self.createWidgets()
        self.setGrid()
        
    
        self.startListener()
        self.processMouseQueue()
        #self.processMouseDisplayQueue()
        self.lastTime = 0
        


        self.root.protocol("WM_DELETE_WINDOW", self.closeApp)


    def testFunc(self):
        self.keyboardControl.type("this is a test type")

    def createFrames(self):
        self.leftFrame = tk.Frame(root)
        self.leftFrame.columnconfigure(0,weight=1)
        self.leftFrame.rowconfigure(0,weight=1)

        self.rightFrame = tk.Frame(root,borderwidth=1,relief="solid")
        self.rightFrame.config(highlightbackground="red",highlightthickness=2)

    def createWidgets(self):
        #Left Frame
        self.eventListLabel = tk.Label(self.leftFrame,text="Events")
        self.eventList = tk.Listbox(self.leftFrame)
        self.update = tk.Button(self.leftFrame,text="Update")
        self.clear = tk.Button(self.leftFrame,text="Clear",command=self.clearList)
        
        #Right Frame
        self.recordHotkeyLabel = tk.Label(self.rightFrame,text="Set Record Hotkey",bg="white",fg="blue",relief="solid",borderwidth=2)
        self.recordHotkey = tk.Button(self.rightFrame,text="ctrl+1", command=self.recordHotKeyStatus)
        self.stopHotkeyLabel = tk.Label(self.rightFrame,text="Stop Hotkey")
        self.stopHotkey = tk.Button(self.rightFrame,text="ctrl+2")
        self.record = tk.Button(self.rightFrame,text="Start Recording",command=self.recordingStatus)
        self.repeatLabel = tk.Label(self.rightFrame,text="Enter number of macro repetitions")
        self.repeat = tk.Entry(self.rightFrame)
        self.speedLabel = tk.Label(self.rightFrame,text="Speed")
        self.speed = tk.OptionMenu(self.rightFrame,"2x","1x")
        self.start = tk.Button(self.rightFrame,text="Run Macro", command=self.macroController)
        self.mousePosVar = tk.StringVar()
        self.mousePosVar.set("Inactive")
        self.mousePosLabel = tk.Label(self.rightFrame,textvariable=self.mousePosVar)
        self.statusVar = tk.StringVar()
        self.statusVar.set("Status: Idle")
        self.statusLabel = tk.Label(self.rightFrame,textvariable=self.statusVar)

    def setGrid(self):
        #frames
        self.leftFrame.grid(row=0,column=0, sticky="nsew")
        self.rightFrame.grid(row=0,column=1, sticky="nsew")

        #Left Frame
        self.eventListLabel.grid(row=0,column=0)
        self.eventList.grid(row=1,column=0,columnspan=2)
        self.update.grid(row=2,column=0)
        self.clear.grid(row=2,column=1)
        
        
        #Right Frame
        self.recordHotkeyLabel.grid(row=0,column=0)
        self.recordHotkey.grid(row=1,column=0)
        self.stopHotkeyLabel.grid(row=0,column=1)
        self.stopHotkey.grid(row=1,column=1)
        self.record.grid(row=3,column=0, columnspan=2)
        self.repeatLabel.grid(row=4, column=0, columnspan=2, pady=(10, 0),sticky="ew")
        self.repeat.grid(row=5,column=0)
        self.speedLabel.grid(row=6,column=0)
        self.speed.grid(row=7,column=0)
        self.start.grid(row=8,column=0)
        self.mousePosLabel.grid(row=8,column=1)
        self.statusLabel.grid(row=9,column=0)

    def clearList(self):
        self.eventList.delete(0,tk.END)
        self.recordedEvents = []


    def startListener(self):
        if self.mouseListener is None or not self.mouseListener.is_alive():
            self.mouseListener = mouse.Listener(on_move=self.mouseMove,
                                           on_click=self.mouseClick)
            self.mouseListener.start()
            #self.mouseListener.stop()
        if self.keyboardListener is None or not self.keyboardListener.is_alive():
            self.keyboardListener = keyboard.Listener(on_press=self.keyboardPress,
                                                      on_release=self.keyboardRelease)
            self.keyboardListener.start()
        if not self.recordGlobalHotkeyListener.running:
            self.recordGlobalHotkeyListener.start()

    def keyboardPress(self,key):
        try:
            if self.isSettingRecordHotKey:
                self.setRecordHotKey(key);
            print("alphanumeric key {0} pressed".format(key.char))
        except AttributeError:
            print("special key {0} pressed".format(key))
            #print(f"special key {key} pressed")
            if key == keyboard.Key.shift:
                print("shift was pressed")
    
    def keyboardRelease(self,key):
        print("{0} released".format(key))
        if key == keyboard.Key.esc:
            return False
        

    #sets the hotkey the moment the first key of the list gets released
    def setRecordHotKey(self,key):
        self.comboLimit = 3
        if len(self.keyHotKeyList) < self.comboLimit:
            keyName = str(key).split(".")[-1]
            self.keyHotKeyList.append(keyName)
        else:
            #self.isSettingRecordHotKey = False
            self.recordHotKeyStatus()




    def recordHotKeyStatus(self):
        if not self.isSettingRecordHotKey:
            self.recordHotkey.config(text="Set Hotkey",fg="red")
            self.keyHotKeyList = []
            self.isSettingRecordHotKey = True
            #self.recordGlobalHotkey = self.getGlobalHotkey()
        else:
            self.isSettingRecordHotKey = False
            self.recordHotkey.config(text=f"{self.recordGlobalHotkey}",fg="black")



    def mouseClick(self,x,y,button,pressed):
        if self.isRecording:
            try:
                self.mouseQueue.put(("click",x,y,button,pressed,time.time()))
            except:
                print(f"error adding {button} click {x},{y}")

    def mouseMove(self,x,y):
        now = time.time()

        """ self.lastMousePos = (x,y)
        if not self.mouseDisplaySchedule:
            self.mouseDisplaySchedule = True
            self.root.after(1000,self.mousePosDisplay) """
            
        if self.isRecording:
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


    """ def processMouseDisplayQueue(self):
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
            self.root.after(100,self.processMouseDisplayQueue) """

        #THIS PRINTS THE X AND Y MOUSE POSITION IN A GUI LABEL
        #BUGGED ON MAC - FREEZING GUI. OK ON WINDOWS
    """ def mousePosDisplay(self):
        if self.lastMousePos:
            x,y = self.lastMousePos
            #print(f"mouse pos currently {int(x)} and {int(y)}")
            self.mousePosVar.set(f"pos at {int(x)} and {int(y)}")
        self.mouseDisplaySchedule = False """


    def recordingStatus(self):
        if not self.isRecording:
            self.startRecording()
        else:
            self.stopRecording()

    def startRecording(self):
        if not self.isRecording:
            print("recording started")
            self.isRecording = True
            self.clearList()
            self.record.config(text="Stop recording",fg="red")
            

    def stopRecording(self):
        if self.isRecording:
            print("recording stopped")
            self.isRecording = False
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



#macro.displayMousePosition()
root = tk.Tk()
app = MouseMacro(root)
root.mainloop()