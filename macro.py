import tkinter as tk

root = tk.Tk()
root.title("Mouse Macro")


frame = tk.Frame(root)
frame.grid(row=0,column=0, sticky="nsew")
frame.columnconfigure(0,weight=1)
frame.rowconfigure(0,weight=1)


eventList = tk.Listbox(frame)
eventList.grid(row=0,column=0,columnspan=2)

update = tk.Button(frame,text="Update")
update.grid(row=1,column=0)

clear = tk.Button(frame,text="Clear")
clear.grid(row=1,column=1)

frame2 = tk.Frame(root,borderwidth=1,relief="solid",highlightbackground="yellow")
frame2.grid(row=0,column=1, sticky="nsew")


recordLabel = tk.Label(frame2,text="Record")
recordLabel.grid(row=0,column=0)

record = tk.Button(frame2,text="Click Me")
record.grid(row=1,column=0)

stopLabel = tk.Label(frame2,text="Stop")
stopLabel.grid(row=0,column=1)

stop = tk.Button(frame2,text="Click Me")
stop.grid(row=1,column=1)

repeatLabel = tk.Label(frame2,text="Repeat")
repeatLabel.grid(row=2, column=0, columnspan=2, pady=(10, 0),sticky="ew")


repeat = tk.Entry(frame2)
repeat.grid(row=3,column=0)

speedLabel = tk.Label(frame2,text="Speed")
speedLabel.grid(row=4,column=0)

speed = tk.OptionMenu(frame2,"2x","1x")
speed.grid(row=5,column=0)

start = tk.Button(frame2,text="Start")
start.grid(row=6,column=0)



root.mainloop()