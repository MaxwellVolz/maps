import cv2
import numpy as np
import pygetwindow as gw
import os
import threading
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode

# Constants
TOGGLE_KEY = KeyCode.from_char("t")  # Key to toggle the scanning and overlay
SCAN_INTERVAL = 5  # Interval in seconds between scans when enabled
MAPS_DIR = "maps"


class ScreenMonitor:
    def __init__(self):
        self.enabled = False
        self.listener = None
        self.loaded_images = self.load_images(MAPS_DIR)

    def load_images(self, search_in_folder):
        images = {}
        for filename in os.listdir(search_in_folder):
            img_path = os.path.join(search_in_folder, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                images[filename] = img
        return images

    def on_press(self, key):
        if key == TOGGLE_KEY:
            self.toggle_feature()

    def start_listener(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def toggle_feature(self):
        self.enabled = not self.enabled
        print(f"Scanning {'enabled' if self.enabled else 'disabled'}")
        if self.enabled:
            self.start_scanning()

    def start_scanning(self):
        if self.enabled:
            threading.Timer(SCAN_INTERVAL, self.start_scanning).start()
            print("Scanning...")
            captured_img = self.capture_screen_area("Your Window Title Here")
            best_match_filename = self.find_best_match(captured_img, self.loaded_images)
            best_match_img_path = os.path.join(MAPS_DIR, best_match_filename)
            self.overlay_image("captured.png", best_match_img_path, 0.5)

    def capture_screen_area(self, title):
        win = gw.getWindowsWithTitle(title)[0]
        win.activate()
        bbox = (win.left, win.top, win.right, win.bottom)
        screen = np.array(gw.screenshot(region=bbox))
        cv2_img = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        cv2.imwrite("captured.png", cv2_img)
        return cv2_img

    def find_best_match(self, template_image, loaded_images):
        w, h = template_image.shape[::-1]
        best_match = None
        max_val = 0
        for filename, img in loaded_images.items():
            res = cv2.matchTemplate(img, template_image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > max_val:
                max_val = max_val
                best_match = filename
        return best_match

    def overlay_image(self, background_img_path, overlay_img_path, opacity):
        background = cv2.imread(background_img_path)
        overlay = cv2.imread(overlay_img_path, cv2.IMREAD_UNCHANGED)
        if overlay.shape[2] == 4:  # Assuming overlay is BGRA
            alpha_overlay = overlay[:, :, 3] / 255.0
            alpha_background = 1.0 - alpha_overlay
            for c in range(0, 3):
                background[:, :, c] = (
                    alpha_overlay * overlay[:, :, c]
                    + alpha_background * background[:, :, c]
                )
        cv2.imshow("Overlayed Image", background)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    monitor = ScreenMonitor()
    monitor.start_listener()
    try:
        while True:  # Keep the main thread alive
            pass
    except KeyboardInterrupt:
        print("Program terminated by user.")
