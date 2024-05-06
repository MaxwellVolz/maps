import cv2
import numpy as np
import pygetwindow as gw
import os
import threading
import keyboard

# Constants
TOGGLE_KEY = "t"  # Key to toggle the scanning and overlay
SCAN_INTERVAL = 5  # Interval in seconds between scans when enabled

# Toggle state
enabled = False

maps_dir = "maps"


def load_images(search_in_folder):
    images = {}
    for filename in os.listdir(search_in_folder):
        img_path = os.path.join(search_in_folder, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images[filename] = img
    return images


def capture_screen_area(title):
    win = gw.getWindowsWithTitle(title)[0]
    win.activate()
    bbox = (win.left, win.top, win.right, win.bottom)
    screen = np.array(gw.screenshot(region=bbox))
    cv2_img = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.imwrite("captured.png", cv2_img)
    return cv2_img


def find_best_match(template_image, loaded_images):
    w, h = template_image.shape[::-1]
    best_match = None
    max_val = 0

    for filename, img in loaded_images.items():
        res = cv2.matchTemplate(img, template_image, cv2.TM_CCOEFF_NORMED)
        _, max_loc, _, _ = cv2.minMaxLoc(res)

        if max_loc > max_val:
            max_val = max_loc
            best_match = filename

    return best_match


def overlay_image(background_img_path, overlay_img_path, opacity):
    background = cv2.imread(background_img_path)
    overlay = cv2.imread(overlay_img_path, cv2.IMREAD_UNCHANGED)

    # Assuming overlay is BGRA
    if overlay.shape[2] == 4:
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


def toggle_feature():
    global enabled
    enabled = not enabled
    if enabled:
        start_scanning()


def start_scanning():
    if enabled:
        captured_img = capture_screen_area("Your Window Title Here")
        best_match_filename = find_best_match(captured_img, loaded_images)
        best_match_img_path = os.path.join(maps_dir, best_match_filename)
        overlay_image("captured.png", best_match_img_path, 0.5)
        threading.Timer(SCAN_INTERVAL, start_scanning).start()


# Bind the key
keyboard.add_hotkey(TOGGLE_KEY, toggle_feature)

# Load images and start if initially enabled
loaded_images = load_images(maps_dir)
if enabled:
    start_scanning()
