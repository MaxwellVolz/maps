from pynput.keyboard import Listener, Key, KeyCode
import threading
import time

# Define key bindings using KeyCode for numpad keys
KEY_START = KeyCode(char="1")
KEY_STOP = KeyCode(char="2")
KEY_EXIT = KeyCode(char="3")


class KeyMonitor:
    def __init__(self):
        self.listener = None
        self.active = False
        self.worker_thread = None

    def on_press(self, key):
        # Start the action thread
        if key == KEY_START:
            if not self.active:
                self.active = True
                self.start_worker_thread()
                print("Worker thread started.")
        # Stop the action thread
        elif key == KEY_STOP:
            if self.active:
                self.stop_worker_thread()
                print("Worker thread stopped.")
        # Exit application and stop action thread
        elif key == KEY_EXIT:
            self.stop_worker_thread()
            self.stop_listener()
            print("Exiting program.")
            return False

    def start_worker_thread(self):
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self.worker_action)
            self.worker_thread.start()

    def stop_worker_thread(self):
        if self.worker_thread:
            self.active = False
            self.worker_thread = None

    def worker_action(self):
        while self.active:
            time.sleep(3)
            print("Action executed every 3 seconds...")

    def start_listener(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None


# Run the monitor
if __name__ == "__main__":
    km = KeyMonitor()
    km.start_listener()  # Start the listener when the script runs
    try:
        while True:  # Keep the main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        km.stop_worker_thread()
        print("Program terminated by user.")
