import time
import pyautogui
from PIL import ImageGrab,Image, ImageTk
import webbrowser
import keyboard
import tkinter as tk
import queue
import threading

def get_pixel_color(x, y):
    screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    return screenshot.getpixel((0, 0))

def calculate_coordinates(screen_width, screen_height):
    x_ratio = 1284 / 2560
    y_ratio = 688 / 1440
    x = int(screen_width * x_ratio)
    y = int(screen_height * y_ratio)
    return x, y

class AutoFishingGUI:
    def __init__(self, root, gui_queue):
        self.root = root
        self.running = False
        self.current_hotkey = 's'
        self.gui_queue = gui_queue
        self.last_detection_time = 0
        self.max_inactive_time = 6
        self.is_closed = False
        self.setup_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        self.root.title("Automated Fishing")
        self.root.geometry("300x200")
        self.root.attributes("-topmost", True)

        self.status_label = tk.Label(self.root, text="Disabled", fg="red")
        self.status_label.pack()

        self.set_hotkey_button = tk.Button(self.root, text="Set New Hotkey", command=self.set_new_hotkey)
        self.set_hotkey_button.pack()

        self.current_hotkey_label = tk.Label(self.root, text=f"Current Hotkey: {self.current_hotkey}")
        self.current_hotkey_label.pack()

        # Footer
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        made_by_label = tk.Label(footer_frame, text="Made by: xFlippy")
        made_by_label.pack(side=tk.LEFT)

        # Load images for buttons
        youtube_img = ImageTk.PhotoImage(Image.open("imgs/youtube.png").resize((20, 20)))
        twitter_img = ImageTk.PhotoImage(Image.open("imgs/twitter.png").resize((20, 20)))
        github_img = ImageTk.PhotoImage(Image.open("imgs/github.png").resize((20, 20)))

        # Buttons with images
        youtube_button = tk.Button(footer_frame, image=youtube_img, command=lambda: webbrowser.open("https://www.youtube.com/channel/UCHIk4-IrVb6351-NjHbrRow"))
        youtube_button.image = youtube_img
        youtube_button.pack(side=tk.LEFT)

        twitter_button = tk.Button(footer_frame, image=twitter_img, command=lambda: webbrowser.open("https://twitter.com/gewoon_aardbei"))
        twitter_button.image = twitter_img
        twitter_button.pack(side=tk.LEFT)

        github_button = tk.Button(footer_frame, image=github_img, command=lambda: webbrowser.open("https://github.com/xflipperkast"))
        github_button.image = github_img
        github_button.pack(side=tk.LEFT)

        keyboard.add_hotkey(self.current_hotkey, lambda: self.gui_queue.put(self.toggle_running))

    def toggle_running(self):
        self.running = not self.running
        status_text = "Running" if self.running else "Paused"
        status_color = "green" if self.running else "red"
        self.status_label.config(text=status_text, fg=status_color)
        self.last_detection_time = time.time()
        if self.running:
            self.check_fishing()

    def set_new_hotkey(self):
        self.set_hotkey_button.config(text="Press a Key...")
        self.current_hotkey_label.config(text="Press a Key...")

        def listen_for_hotkey():
            new_hotkey = keyboard.read_hotkey(suppress=False)
            self.gui_queue.put(lambda: self.update_hotkey(new_hotkey))

        threading.Thread(target=listen_for_hotkey, daemon=True).start()

    def update_hotkey(self, new_hotkey):
        if new_hotkey:
            keyboard.remove_hotkey(self.current_hotkey)
            self.current_hotkey = new_hotkey
            keyboard.add_hotkey(self.current_hotkey, lambda: self.gui_queue.put(self.toggle_running))
            self.current_hotkey_label.config(text=f"Current Hotkey: {self.current_hotkey}")
            self.set_hotkey_button.config(text="Set New Hotkey")

    def on_closing(self):
        self.running = False
        self.is_closed = True
        self.root.destroy()
        keyboard.unhook_all_hotkeys()

    def check_fishing(self):
        if not self.running:
            self.root.after(1000, self.check_fishing)
            return

        x, y = calculate_coordinates(pyautogui.size().width, pyautogui.size().height)
        current_color = get_pixel_color(x, y)
        target_color = (112, 237, 252)

        if current_color == target_color:
            pyautogui.click()
            self.root.after(100, lambda: self.perform_click_sequence(x, y, target_color))
        elif time.time() - self.last_detection_time > self.max_inactive_time:
            pyautogui.click()
            self.last_detection_time = time.time()
            self.root.after(1000, self.check_fishing)
        else:
            self.root.after(100, self.check_fishing)

    def perform_click_sequence(self, x, y, target_color):
        if not self.running or get_pixel_color(x, y) != target_color:
            self.root.after(500, lambda: self.finish_click_sequence(x, y))
            return
        pyautogui.click()
        self.root.after(100, lambda: self.perform_click_sequence(x, y, target_color))

    def finish_click_sequence(self, x, y):
        if not self.running:
            self.check_fishing()
            return
        pyautogui.click()
        self.root.after(4500, lambda: self.second_click_in_sequence(x, y))

    def second_click_in_sequence(self, x, y):
        if self.running:
            pyautogui.click()
            self.last_detection_time = time.time()
        self.check_fishing()

def main():
    root = tk.Tk()
    gui_queue = queue.Queue()
    gui = AutoFishingGUI(root, gui_queue)

    while True:
        if gui.is_closed:
            break

        try:
            func = gui_queue.get_nowait()
            func()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"An error occurred: {e}")
            break

        try:
            root.update()
            root.update_idletasks()
        except tk.TclError:
            break

if __name__ == "__main__":
    main()
