# save this as test_pynput_caps.py
import sys
from pynput import keyboard
import time

print(f"--- System Info ---")
print(f"Python: {sys.version}")
try:
    import pynput
    print(f"pynput: {pynput.__version__}")
except ImportError:
    print("pynput not found!")
    sys.exit(1)
except Exception as e:
    print(f"Error importing or getting pynput version: {e}")


def on_release(key):
    try:
        print(f'{time.time()} - Released: {key}')
        if key == keyboard.Key.caps_lock:
            print(f'--- Caps Lock Release Detected ---')
            # We don't even need to return here; just printing is enough.
            # If it crashes AFTER this print, the issue is likely
            # when control returns from this function back to pynput.
    except Exception as e:
        print(f"Error inside on_release callback: {e}")

print("\nStarting pynput listener... Press keys (especially Caps Lock) and then Ctrl+C to exit.")

listener = None
try:
    # Start listener in a separate thread
    listener = keyboard.Listener(on_release=on_release)
    listener.start()
    # Keep the main thread alive until interrupted
    listener.join()
except KeyboardInterrupt:
    print("\nCtrl+C detected. Stopping listener...")
except Exception as e:
    print(f"\nAn error occurred during listener setup or join: {e}")
finally:
    if listener and listener.is_alive():
        print("Listener stopping...")
        listener.stop()
        # listener.join() # Ensure thread finishes
        print("Listener stopped.")
    else:
        print("Listener already stopped or not started.")

print("Script finished.")