
import os
import settings
from services import WebAccess
from services import Log
from time import sleep
from win10toast_click import ToastNotifier
import pyperclip
import subprocess
import tkinter as tk
from tkinter import ttk
import winsound
from PIL import Image, ImageTk, ImageFilter
import threading
class LateAlert:
    def __init__(self, db):
        self.db = db
        self.toaster = ToastNotifier()

    def start_requests(self, playwright):
        with WebAccess(playwright, settings.playwright_headless, settings.profile) as web_access:
            
            # web_access.start_context(settings.goto_url, "")

            late = self.get_late_reservations(web_access)
            if late:
                
                for reservation in late:                      
                    self.show_toast("Late Alert", reservation)

            else:
                self.show_toast("Late Alert", "No late reservations", 'boC2gLogo.jpg')

    def get_late_reservations(self, web_access: WebAccess):
        """
        This function checks for late reservations.
        :param web_access: WebAccess instance
        :return: List of late reservations
        """

        return {locator.text_content() for locator in web_access.query_locator_all("#billingReceipetSpan h3")}
    


    def show_toast(self, title, message, icon_path=None, sound_path=None):
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)  # Start transparent

        # Size and position
        width, height = 320, 120
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        final_x = screen_width - width - 20
        final_y = screen_height - height - 60
        start_y = final_y + 100
        root.geometry(f"{width}x{height}+{final_x}+{start_y}")

        # Optional sound
        if sound_path and os.path.exists(sound_path):
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        # Canvas for rounded corners
        canvas = tk.Canvas(root, width=width, height=height, bg='white', bd=0, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        radius = 20
        canvas.create_rectangle(0, 0, width, height, outline="", fill="#fefefe")
        canvas.create_arc((0, 0, radius*2, radius*2), start=90, extent=90, fill="#fefefe", outline="#fefefe")
        canvas.create_arc((width - radius*2, 0, width, radius*2), start=0, extent=90, fill="#fefefe", outline="#fefefe")
        canvas.create_arc((0, height - radius*2, radius*2, height), start=180, extent=90, fill="#fefefe", outline="#fefefe")
        canvas.create_arc((width - radius*2, height - radius*2, width, height), start=270, extent=90, fill="#fefefe", outline="#fefefe")



        # Frame inside canvas
        content = tk.Frame(canvas, bg="#fefefe")
        canvas.create_window((70, 10), window=content, anchor='nw')

        ttk.Label(content, text=title, font=("Segoe UI", 12, "bold"), background="#fefefe").pack(anchor="w")
        ttk.Label(content, text=message, font=("Segoe UI", 10), background="#fefefe", wraplength=220, justify="left").pack(anchor="w", pady=(0, 10))

        ttk.Button(
            content,
            text="Copy",
            command=lambda: (pyperclip.copy(message), root.destroy())
        ).pack(anchor="e")

        # Animation: fade-in and slide-in
        def animate(alpha=0.0, y=start_y):
            if alpha < 0.95 or y > final_y:
                alpha = min(alpha + 0.05, 0.95)
                y = max(y - 5, final_y)
                root.attributes("-alpha", alpha)
                root.geometry(f"{width}x{height}+{final_x}+{y}")
                root.after(25, lambda: animate(alpha, y))

        animate()
        root.after(8000, root.destroy)
        root.mainloop()
