from pynput import keyboard
import time

def run_listener(raw_queue):
    def on_press(key):
        raw_queue.put(("keyPress", key,time.time()))
    def on_release(key):
        raw_queue.put(("keyRelease", key,time.time()))

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
