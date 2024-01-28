import time
import pyautogui
from PIL import ImageGrab
import keyboard

def get_pixel_color(x, y):
    screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    pixel_color = screenshot.getpixel((0, 0))
    return pixel_color

def calculate_coordinates(screen_width, screen_height):
    x_ratio = 1284 / 2560
    y_ratio = 688 / 1440
    x = int(screen_width * x_ratio)
    y = int(screen_height * y_ratio)
    return x, y

def main():
    # Cool text message by xFlippy
    print("=========================================")
    print(" Automated fishing by xFlippy")
    print(" happy autofishing!")
    print("=========================================")

    screen_width, screen_height = pyautogui.size()
    target_coords = calculate_coordinates(screen_width, screen_height)

    target_color = (112, 237, 252)
    check_interval = 1
    max_inactive_time = 6
    last_detection_time = 0
    running = False

    def toggle_running():
        nonlocal running
        running = not running
        status = "Running" if running else "Paused"
        print(f"{status}. Press 's' to start/pause.")

    keyboard.add_hotkey('s', toggle_running)

    print("AutoFish. Press 's' to start/pause.")

    while True:
        if running:
            current_color = get_pixel_color(*target_coords)

            if current_color == target_color:
                print("Color matched. Starting continuous left click actions...")

                while running and get_pixel_color(*target_coords) == target_color:
                    pyautogui.click()
                    time.sleep(0.1)

                print("Color disappeared. Waiting 0.5 seconds and clicking again...")

                time.sleep(0.5)
                pyautogui.click()

                time.sleep(4.5)
                pyautogui.click()

                last_detection_time = time.time()

            elif time.time() - last_detection_time > max_inactive_time:
                print("Target color not detected for more than 6 seconds. Clicking once...")
                pyautogui.click()
                last_detection_time = time.time()

        time.sleep(check_interval)

if __name__ == "__main__":
    main()
