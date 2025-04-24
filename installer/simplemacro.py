import tkinter as tk
import tkinter.ttk as ttk
from pynput import mouse,keyboard
import queue
import time
import threading
import sys,ctypes



class MouseMacro:
    def __init__(self,root):
        self.root = root
        self.root.title("Simple Macro")
        self.root.configure(bg="#23272e")

        self.style = ttk.Style()
        self.style.configure("RedText.TButton",foreground="red")

        self.recordedEvents = []

        self.OS = sys.platform

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
        self.vkMappingEnabled = False
        self.keyboardControl = keyboard.Controller()
        self.keyboardQueue = queue.Queue()
        self.keyboardListener = None
        self.recordGlobalHotkey = "<ctrl>+@"
        self.globalHotkeyListener = None
        self.isSettingHotkey = False
        self.currentSettingHotkey = None
        self.keyHotkeyList = []
        self.listString = ""
        self.recordingControlKey = False
        self.currentKeys = set()
        self.awaitingHotkey = False
        self.hotkeyModifier = None

        #MAIN MACRO CONTROLS
        self.isRecording = False
        self.macroRunning = False
        self.totalRepetitions = 0
        self.currentRepetitions = 0
        self.currentEventIndex = 0
        self.nextPlayback = None
        self.listEventsIndex = 0


        #OS Setup
        self.determineOS()

        #GUI SETUP
        self.createFrames()
        self.createWidgets()
        self.setGrid()
        
    
        self.startListener()
        self.processMouseQueue()
        self.processKeyboardQueue()
        #self.processMouseDisplayQueue()
        self.lastTime = 0
        

        #threading.Thread(target=self.debugKeyEvents, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.closeApp)


    def testFunc(self):
    
        self.keyboardControl.type("this is a test type")

    def debugKeyEvents(self):
        print("Debug: Listening for raw key events...")
        with keyboard.Events() as events:
            for event in events:
                print(f"Event: {event}")

    def determineOS(self):
        if self.OS == "win32":
            self.initializeWindowsKeyMapping()
        """ elif self.OS == "darwin":
            self.initializeMacKeyMapping() """


    def initializeWindowsKeyMapping(self):
        
        try:
            from ctypes import wintypes

            self.user32 = ctypes.WinDLL('user32', use_last_error=True)

            # Set up function prototypes
            self.GetKeyboardLayout = self.user32.GetKeyboardLayout
            self.GetKeyboardLayout.argtypes = [wintypes.DWORD]
            self.GetKeyboardLayout.restype = wintypes.HKL

            self.MapVirtualKeyEx = self.user32.MapVirtualKeyExW
            self.MapVirtualKeyEx.argtypes = [wintypes.UINT, wintypes.UINT, wintypes.HKL]
            self.MapVirtualKeyEx.restype = wintypes.UINT

            self.GetKeyboardState = self.user32.GetKeyboardState
            self.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte * 256)]
            self.GetKeyboardState.restype = wintypes.BOOL

            self.ToUnicodeEx = self.user32.ToUnicodeEx
            self.ToUnicodeEx.argtypes = [
                wintypes.UINT, wintypes.UINT,
                ctypes.POINTER(ctypes.c_ubyte * 256),
                wintypes.LPWSTR, ctypes.c_int,
                wintypes.UINT, wintypes.HKL
            ]
            self.ToUnicodeEx.restype = ctypes.c_int

            # Constants
            self.VK_CONTROL = 0x11
            self.MAPVK_VK_TO_VSC = 0
            
            self.vkMappingEnabled = True
            print("Windows virtual key mapping initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Windows virtual key mapping: {e}")


    def createFrames(self):
        self.leftFrame = tk.Frame(root)
        self.buttonFrame = tk.Frame(self.leftFrame)

        self.rightFrame = tk.Frame(root)

    def createWidgets(self):
        #Left Frame
        self.eventListLabel = ttk.Label(self.leftFrame,text="Events",anchor="center")
        self.eventList = tk.Listbox(self.leftFrame,width=50)
        self.eventListScrollbar = ttk.Scrollbar(self.leftFrame, orient=tk.VERTICAL, command=self.eventList.yview)
        self.eventList.config(yscrollcommand=self.eventListScrollbar.set)

        
        #self.update = ttk.Button(self.buttonFrame,text="Update")
        self.clear = ttk.Button(self.buttonFrame,text="Clear",command=self.clearListButton)
        
        #Right Frame
        self.recordHotkeyLabel = ttk.Label(self.rightFrame,text="Set Record Hotkey",anchor="center")
        self.recordHotkey = ttk.Button(self.rightFrame,text="click to set", command= lambda: self.setHotkeyMode("record"))
        self.stopMacroLabel = ttk.Label(self.rightFrame,text="Stop Macro",anchor="center")
        self.stopMacroButton = ttk.Button(self.rightFrame,text="click to set", command= lambda: self.setHotkeyMode("stop"))
        self.record = ttk.Button(self.rightFrame,text="Start Recording",command=self.recordingStatus)
        self.repeatLabel = ttk.Label(self.rightFrame,text="Enter number of macro repetitions",anchor="center")
        self.repeat = ttk.Entry(self.rightFrame)
        self.speedLabel = ttk.Label(self.rightFrame,text="Speed",anchor="center")
        self.speedVar = tk.StringVar()
        self.speedVar.set("1x")
        self.speed = ttk.Combobox(self.rightFrame,textvariable=self.speedVar,values=["1x","2x"],state="readonly",justify="center")
        self.start = ttk.Button(self.rightFrame,text="Run Macro", command=self.macroController)
        #self.mousePosVar = tk.StringVar()
        #self.mousePosVar.set("Inactive")
        #self.mousePosLabel = tk.Label(self.rightFrame,textvariable=self.mousePosVar)
        self.statusVar = tk.StringVar()
        self.statusVar.set("Status: Idle")
        self.statusLabel = ttk.Label(self.rightFrame,textvariable=self.statusVar,anchor="center")

    def setGrid(self):

        #root configs
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1,weight=0)
        root.rowconfigure(0,weight=1)

        #frames
        self.leftFrame.grid(row=0,column=0, sticky="nsew")
        self.rightFrame.grid(row=0,column=1, sticky="ns")
        self.buttonFrame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.buttonFrame.columnconfigure(0, weight=1)
        self.buttonFrame.columnconfigure(1, weight=0)
        self.buttonFrame.columnconfigure(2, weight=1)
        self.buttonFrame.rowconfigure(0, weight=0)

        #Left Frame
        self.leftFrame.columnconfigure(0, weight=1) 
        self.leftFrame.columnconfigure(1, weight=1)

        self.leftFrame.rowconfigure(0,weight=0) 
        self.leftFrame.rowconfigure(1, weight=1)
        self.leftFrame.rowconfigure(2,weight=0) 


        self.eventListLabel.grid(row=0,column=0,columnspan=2,sticky="ew")
        self.eventList.grid(row=1,column=0,columnspan=2,sticky="nswe")
        self.eventListScrollbar.grid(row=1,column=3,sticky='ns')
        #self.update.grid(row=0, column=1, padx=5, pady=5)
        self.clear.grid(row=0, column=1)

        
        #Right Frame
        self.rightFrame.rowconfigure(8, weight=1)
        self.rightFrame.rowconfigure(9, weight=0)

        self.recordHotkeyLabel.grid(row=0,column=0,sticky="ew")
        self.recordHotkey.grid(row=1,column=0,sticky="ew")
        self.record.grid(row=2,column=0,sticky="ew")
        self.repeatLabel.grid(row=3, column=0,sticky="ew")
        self.repeat.grid(row=4,column=0,sticky="ew")
        self.speedLabel.grid(row=5,column=0,sticky="ew")
        
        self.speed.grid(row=6,column=0,sticky="ew")
        self.start.grid(row=7,column=0,sticky="ew")
        #self.mousePosLabel.grid(row=8,column=1)
        self.statusLabel.grid(row=9,column=0,sticky="nsew")


    def clearListButton(self):
        self.clearList()
        self.listEventsIndex = 0
        if self.isRecording:
            self.stopRecording()

    def clearList(self):
        self.eventList.delete(0,tk.END)
        self.recordedEvents = []
       

    """#hotkey listener needs to be restarted everytime a new hotkey is set
    #as it only stores the values when created
    def setGlobalHotkeyListener(self):
        try:
            if self.globalHotkeyListener and self.globalHotkeyListener.running:
                self.globalHotkeyListener.stop()
                self.globalHotkeyListener.join(timeout=0.5)
                self.checkListenerIsDead()
            else:
                self.startGlobalHKlistener()
        except Exception as e:
            print(f"global hotkey listener crashed {e}")

    def checkListenerIsDead(self):
        if self.globalHotkeyListener and self.globalHotkeyListener.is_alive():
            print("old listener still alive")
            self.root.after(50,self.checkListenerIsDead)
        else:
            print("old listener has stopped")
            self.globalHotkeyListener = None
            self.startGlobalHKlistener()

    def startGlobalHKlistener(self):
        try:
            self.globalHotkeyListener = keyboard.GlobalHotKeys({
                    self.recordGlobalHotkey:self.recordingStatus})
            self.globalHotkeyListener.start()
        except Exception as e:
            print(f"global hotkey listener crashed {e}") """

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

    def keyboardPress(self,key):
        #print(key)
        try:
            if self.isSettingHotkey:
                self.collectHotkeyKey(key,"keyPress");

            
            action = self.hotkeyManager(key,"keyPress")

            if action == "catch":
                return
            
            elif action == "pass":
                if self.isRecording:
                    self.keyboardQueue.put(("keyPress",key,time.time()))
                #print(f"pressed {self.getKeyName(key)}")
        except Exception as e:
            print(f"error when pressing {e}")
    
    def keyboardRelease(self,key):

        try:
            if self.isSettingHotkey:
                self.collectHotkeyKey(key,"keyRelease")
                return;

            print(f"released {key}")
            self.hotkeyManager(key,"keyRelease")

            if self.isRecording and not self.isHotkey:
                self.keyboardQueue.put(("keyRelease",key,time.time()))

            #print(f"released {self.getKeyName(key)}")
       
        except Exception as e:
            print(f"error when releasing {e}")
        


    def hotkeyManager(self,key,keyType):

        keyName = self.getKeyName(key)
        currentHotkey = self.comboSet()

        if keyType == "keyPress":
            if not self.currentKeys:
                if keyName in currentHotkey and isinstance(key,keyboard.Key) :
                    self.currentKeys.add(keyName)
                else:
                    self.currentKeys.clear()

            if len(self.currentKeys) == 1:
                if keyName in currentHotkey and keyName not in self.currentKeys:
                    self.currentKeys.add(keyName)

            elif len(self.currentKeys) == 2:
                self.currentKeys.clear()
            print(f"current combo {self.currentKeys}")
            if self.comboSet() == self.currentKeys:
                self.recordingStatus()
                return
                
        if keyType == "keyRelease":
            self.currentKeys.discard(keyName)
            print(f"combo after discard {self.currentKeys}")
            return


    def setHotkeyMode(self, hotkeyType):
        if self.isSettingHotkey:
            self.isSettingHotkey = False
            self.recordHotkey.config(text=self.recordGlobalHotkey)
            return
            #self.recordGlobalHotkey = self.getGlobalHotkey()
        if not self.isRecording:
            self.isSettingHotkey = True
            self.currentSettingHotkey = hotkeyType
            self.keyHotkeyList = []

            if hotkeyType == "record":
                self.recordHotkey.config(text="Press Keys",style="RedText.TButton")
                self.statusVar.set("Press keys for record hotkey")


    def comboSet(self):
        return{
            part.strip("<>").lower()
            for part in self.recordGlobalHotkey.split("+")
        }

    def collectHotkeyKey(self, key, keyType):
        print("entered collect")
        try:
            listLength = len(self.keyHotkeyList)
            print("checking length")

            if keyType == "keyRelease":
                if listLength == 0:
                    self.isSettingHotkey = False
                    self.currentSettingHotkey = None
                    self.setHotkeyMode("end")
                else:
                    self.finalizeHotkey()
                
                return

            else:

                if listLength == 0:
                    if isinstance(key,keyboard.Key):
                        self.keyHotkeyList.append(key)
                
                elif listLength == 1:
                    self.keyHotkeyList.append(key)
                    self.finalizeHotkey()
                print("reached collect bottom")
                
        except Exception as e:
            print(f"Error collecting hotkey: {e}")
            self.finalizeHotkey()  # Finalize anyway to avoid getting stuck

    def finalizeHotkey(self):
        # Create hotkey string in pynput format: <ctrl>+a
        hotkey_str = ""
        print("inside finalize hotkey")
        if self.keyHotkeyList:
            for i, key in enumerate(self.keyHotkeyList,start=1):
                print("inside loop")
                #special keys
                print("getting name")
                keyName = self.getKeyName(key)
                print("name obtained")
                if isinstance(key,keyboard.Key):
                    hotkey_str += f"<{keyName}>"
                else:
                    hotkey_str += keyName
                
                if i < len(self.keyHotkeyList):  # Add + between keys
                    hotkey_str += "+"
            
            # Apply the hotkey
            if self.currentSettingHotkey == "record":
                self.recordGlobalHotkey = hotkey_str
                self.recordHotkey.config(text=hotkey_str, style="TButton")
        
            
        # Reset state
        self.isSettingHotkey = False
        self.currentSettingHotkey = None
        self.keyHotkeyList = []
        
        #print(self.recordGlobalHotkey)
        self.statusVar.set(f"Hotkey set to {self.recordGlobalHotkey}")
        #self.root.after(1000, self.setGlobalHotkeyListener)


    def getKeyName(self,key):
        #CHARS
        #print(key)
        if isinstance(key,keyboard.KeyCode):
            print(f"vk is {key.vk}")
            #charToVk = self.vkToChar(key.vk)
            #print(f"converted vk is {charToVk}")

            if (key.char is None or not key.char.isprintable()) and self.vkMappingEnabled:

                print("key is not printable")
                return self.vkToChar(key.vk)
            else:
                print("key is printable")
                return key.char
            
      
            #return key.char if key.char is not None else self.vkToChar(key.vk)
        #control keys
        else:
            #print(f"control key {key}")
            """ if key in self.modifierDisplayMap:
                return self.modifierDisplayMap[key][0]
            else:
                #print(key.value) """
            keyName = str(key).split(".")[-1]
            if '_' in keyName:
                keyName = keyName.split("_")[0]
            print(f"keyname is {keyName}")
            return keyName

    def vkToChar(self,vk):
        
        if self.OS == "win32":    
            try:
                hkl = self.GetKeyboardLayout(0)
                sc = self.MapVirtualKeyEx(vk, self.MAPVK_VK_TO_VSC, hkl)
                state = (ctypes.c_ubyte * 256)()
                self.GetKeyboardState(ctypes.byref(state))
                # Clear Ctrl so the API will still return the "real" character
                state[self.VK_CONTROL] = 0
                buf = ctypes.create_unicode_buffer(4)
                rc = self.ToUnicodeEx(vk, sc, state, buf, len(buf), 0, hkl)
                return buf.value if rc > 0 else ''
            except Exception as e:
                print(f"Error in vk_to_char: {e}")
                return None
            

        elif self.OS == "darwin":
            try:
                src = self.TISCopyCurrentKeyboardLayoutInputSource()
                data = self.TISGetInputSourceProperty(src, self.kTISPropertyUnicodeKeyLayoutData)
                layout = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint8))
                dead = ctypes.c_uint32(0)
                buf = (ctypes.c_uint16 * 4)()
                length = ctypes.c_size_t()
                self.UCKeyTranslate(
                    layout, vk, self.kUCKeyActionDisplay, 0,
                    self.LMGetKbdType(), self.kUCKeyTranslateNoDeadKeysMask,
                    ctypes.byref(dead), 4, ctypes.byref(length), buf
                )
                return ''.join(chr(buf[i]) for i in range(length.value))
            except Exception as e:
                print(f"Error in vk_to_char_mac: {e}")
                return None

    def processKeyboardQueue(self):
        try:
            while True:
                eventData = self.keyboardQueue.get_nowait()
                eventType, key, _ = eventData
                keyName = self.getKeyName(key)
                
                # Add to recorded events list
                self.recordedEvents.append(eventData)
                #print("event data received")
                self.firstControlKey = None

                # Update UI
                if eventType == "keyPress":
                        if isinstance(key,keyboard.KeyCode):
                            print(f"checking control key {key.char}")
                            self.listString += keyName
                            self.addToListEvent(eventType,self.listString)
                        else:
                            self.recordingControlKey = True

                            if self.firstControlKey is None:
                                self.firstControlKey = keyName

                            if self.listString: 
                                self.listEventsIndex +=1
                                self.listString = ""
                            self.listString += keyName
                #keyRelease
                else:
                    if isinstance(key,keyboard.Key):
                        if keyName == self.firstControlKey:
                            self.firstControlKey = None
                        self.recordingControlKey = False
                        #self.addToListEvent(eventType,self.listString)
                        self.listEventsIndex+=1
                        self.listString = ""
              

        except queue.Empty:
            pass
        finally:
            # Schedule the next check
            self.root.after(100, self.processKeyboardQueue)
    
    def addToListEvent(self,eventType,item):
        
        if eventType == "keyPress":
            self.eventList.delete(self.listEventsIndex)
        

            
        self.eventList.insert(self.listEventsIndex,f"{item}")
        self.eventList.see(tk.END)


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
                        if self.listString:
                            self.listEventsIndex +=1
                            self.listString = ""
                        self.addToListEvent(eventType,f"click {button} at x: {int(x)}, y: {int(y)}")
                        self.listEventsIndex +=1
                        #self.eventList.insert(tk.END,f"click {button} at x: {int(x)}, y: {int(y)}")

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
        if not self.isRecording and not self.isSettingHotkey:
            self.startRecording()
        else:
            self.stopRecording()
        
        self.root.focus_set()

    def startRecording(self):
        if not self.isRecording:
            print("recording started")
            self.isRecording = True
            self.clearList()
            self.record.config(text="Stop recording", style="RedText.TButton")
            

    def stopRecording(self):
        if self.isRecording:
            print("recording stopped")
            self.isRecording = False
            self.record.config(text="Start recording",style="TButton")

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
           self.start.config(text="Stop Macro", style="RedText.TButton")
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
        self.start.config(text="Run Macro",style="TButton")
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
        elif eventType == "keyPress":
            _, key, _ = currentEvent
            self.keyboardControl.press(key)
        elif eventType == "keyRelease":
            _, key, _ = currentEvent
            self.keyboardControl.release(key)
        
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
        self.start.config(text="Run Macro",style="TButton")

    def closeApp(self):
        if self.mouseListener and self.mouseListener.is_alive():
            self.mouseListener.stop()

        self.root.destroy()



#macro.displayMousePosition()
root = tk.Tk()
app = MouseMacro(root)
root.mainloop()