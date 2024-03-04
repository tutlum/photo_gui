import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import ttk
import json
import deploytowebsite

class GPhoto2GUI:

    def __exit__(self):
        self.disconnect_camera()

    def __init__(self, root, live=True):
        with open('config.json') as f:
            self.config = json.load(f)

        self.live = live

        if (not os.path.isdir("images")):
            os.mkdir("images")
        if (not os.path.isdir("gallery")):
            os.mkdir("gallery")
        self.last_picture=None

        self.capture_text="neues Foto machen (5s Timer)"

        self.root = root
        self.root.title("GPhoto2 GUI")
        self.root.configure(background='black')

        # Make the window full screen
        self.root.attributes('-fullscreen', True)

        self.status=""

        # Configure grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        if self.live: self.connect_camera() 

        # Style for buttons
        style = ttk.Style()
        style.configure('TButton', font=("Quiksand", 30), padding=40, background='#222222', foreground='white')
        style.configure('.', background='black', foreground='white')


        # Capture Photo Button
        self.capture_button = ttk.Button(root, text=self.capture_text, command=self.start_timer)
        self.capture_button.grid(row=0, column=0, columnspan=2, sticky="ew")


        # Disconnect Button
        # self.disconnect_button = ttk.Button(root, text="Disconnect", command=self.disconnect_camera)
        # self.disconnect_button.grid(row=0, column=2, sticky="ew")

         # Countdown timer
        self.timer_label = ttk.Label(root, text="", font=("Arial", 100))
        self.timer_label.grid(row=1, column=0, sticky="ns")

        self.photo_label = ttk.Label(root)
        self.photo_label.grid(row=2, column=0, sticky="ns")

        # Delete Button
        self.delete_button = ttk.Button(root, text="lösche aktuelles Foto", command=self.delete_last)
        self.delete_button.grid(row=2, column=1, sticky="ew")
        self.delete_button.grid_forget()


        # Bind space key to capture photo
        root.bind("<space>", lambda event: self.start_timer())
        root.bind("<s>", lambda event: self.start_timer())
        root.bind("<odiaeresis>", lambda event: self.delete_last())

        # Bind ESC key to exit
        root.bind("<Escape>", lambda event: self.exit_app())

    def run_command(self, command):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr)
            return None

    def connect_camera(self):
        command = ["gphoto2", "--auto-detect"]
        output = self.run_command(command)
        if output:
            messagebox.showinfo("Connected", "Camera connected successfully.")
        else:
            messagebox.showerror("Error", "Failed to connect to camera.")

    def disconnect_camera(self):
        command = ["gphoto2", "--reset"]
        output = self.run_command(command)
        if output:
            messagebox.showinfo("Disconnected", "Camera disconnected successfully.")
        else:
            messagebox.showerror("Error", "Failed to disconnect from camera.")

    def start_timer(self):
        if (self.status!="process"):
            self.save_image()
            self.status="process"
            self.timer_count = self.config["countdown"]  # 5 seconds countdown
            self.update_timer()
        

    def update_timer(self):
        if self.timer_count > 0:
            self.timer_label.config(text="{}".format(self.timer_count))
            self.timer_count -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="SMILE")
            self.root.after(100, self.capture_photo)

    def capture_photo(self):
        filename = os.path.join("images", datetime.now().strftime("%d%H%M%S") + ".jpg")
        command = ["gphoto2", "--capture-image-and-download", "--filename", filename ]
        
        self.timer_label.config(text="lade ...")
        if self.live: output = self.run_command(command)
        else:
            output = "yes"
            self.run_command(["cp", "assets/corvids.jpg", filename])
        self.timer_label.config(text="")
        print(output)
        if output:
            #messagebox.showinfo("Photo Captured", "Photo captured successfully.")
            self.display_last_photo(filename)

    def display_last_photo(self, filename):
        # Check if the last photo exists
        self.last_picture = os.path.join(os.getcwd(), filename)
        self.start_timer_hide()
        self.capture_button.grid(row=0, column=0, columnspan=2, sticky="ew")
        if os.path.exists(self.last_picture):
            # Load the image and display it
            image = Image.open(self.last_picture)
            # Resize image to fit window width
            window_height = self.root.winfo_height()
            image = image.resize((int(window_height*0.75*image.width/image.height), int(window_height*0.75)))
            photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=photo)
            self.photo_label.image = photo
        elif self.live:
            messagebox.showwarning("Warning", f"No photo available: {self.last_picture}")

    def delete_last(self):
        if self.status=="save":
            if self.live and os.path.exists(self.last_picture): 
                os.remove(self.last_picture)
            print(f"delete {self.last_picture}")
            self.clear_all()

    def start_timer_hide(self):
        self.status="save"
        self.capture_button.config(text="speichern und "+self.capture_text)
        self.delete_button.grid(row=2, column=1, sticky="ew")
        self.timer_count_hide = 20  # 20 seconds countdown
        self.update_timer_hide()

    def update_timer_hide(self):
        if self.timer_count_hide > 0:
            self.timer_label.config(text="Speichere Foto in {}s".format(self.timer_count_hide))
            self.timer_count_hide -= 1
            self.root.after(1000, self.update_timer_hide)
        elif self.timer_count_hide == 0:
            self.save_image()
    
    def save_image(self):
        if (self.last_picture!=None and os.path.isfile(self.last_picture)):
            os.rename(self.last_picture, self.last_picture.replace("/images/", "/gallery/"))
        self.clear_all()
    
    def clear_all(self):
        self.timer_count_hide=-1
        self.timer_label.config(text="")
        self.photo_label.config(image=None)
        self.photo_label.image = None
        self.delete_button.grid_forget()
        self.capture_button.config(text=self.capture_text)
        self.status=""
        self.last_picture=None



    def exit_app(self):
        self.root.quit()



if __name__ == "__main__":
    root = tk.Tk()
    live = True
    if (len(sys.argv)>1): live = sys.argv[1]=="live"
    app = GPhoto2GUI(root, live)
    root.mainloop()
