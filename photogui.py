import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import ttk
import json
from deploytowebsite import to_website
import multiprocessing

from tkinter import *
import cv2 
from PIL import Image, ImageTk 
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
file_handler = logging.FileHandler('logfile.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

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

        self.capture_text=f"neues Foto machen\n({self.config["countdown"]}s Timer)"

        self.info_text=self.config["texts"]["info"]
        self.delete_info_text=self.config["texts"]["delete_info"]

        self.root = root
        self.root.title("GPhoto2 GUI")
        self.root.configure(background='white')

        # Make the window full screen
        self.root.attributes('-fullscreen', True)

        self.setstatus("")
        self.webcam="on"

        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=8)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_columnconfigure(2, weight=1)

        if self.live: self.connect_camera() 

        font=self.config["font"]

        # Style for buttons
        style = ttk.Style()
        style.configure('TButton', font=(font, 40), padding=(20,70,20,10), background='#EEEEEE', foreground='black', anchor="center", justify="center")
        style.configure('TLabel', font=(font, 40), padding=(20,70,20,10), background='white', foreground='black', anchor="center", justify="center")
        style.configure('Picture.TLabel', font=(font, 50), padding=0, background='white', foreground='black', anchor="top", justify="center")
        style.configure('.', background='white', foreground='black')


        # Capture Photo Button
        self.capture_button = ttk.Button(root, text=self.capture_text, command=self.start_timer)
        #self.capture_button.config(wraplength=width/5-20)
        self.capture_button.grid(row=2, column=0, columnspan=1, sticky="ews")

        # Delete Button
        self.delete_button = ttk.Button(root, text="lösche\naktuelles Foto", command=self.delete_last)
        self.delete_button.grid(row=2, column=2, sticky="ews")
        self.delete_button.config(state="disable")
        #self.delete_button.grid_forget()
        self.explain=ttk.Label(root, text=self.info_text, font=(font, 40))
        self.explain.grid(row=2, column=1, columnspan=1, sticky="ewn")

        # Disconnect Button
        # self.disconnect_button = ttk.Button(root, text="Disconnect", command=self.disconnect_camera)
        # self.disconnect_button.grid(row=0, column=2, sticky="ew")

         # Countdown timer
        self.timer_label = ttk.Label(root, text="", font=(font, 80))
        self.timer_label.grid(row=0, column=0, columnspan=3, sticky="ns")

        self.photo_label = ttk.Label(root,style='Picture.TLabel')
        self.photo_label.grid(row=1, column=1, columnspan=1, sticky="ewn")


        # preview
        self.vid = cv2.VideoCapture(0) 
        # Declare the width and height in variables 
        #self.label_webcam = ttk.Label(root) 
        #self.label_webcam.grid(rrow=1, column=0, columnspan=2, sticky="ns")
        self.photo_label.after(50,self.start_webcam)


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
        if (self.status!="process" and self.status!="timer"):
            self.save_image()
            self.setstatus("timer")
            self.timer_count = self.config["countdown"]  # 5 seconds countdown
            self.update_timer()
        

    def update_timer(self):
        if self.timer_count > 0:
            self.timer_label.config(text="{}".format(self.timer_count))
            self.timer_count -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.setstatus("process")
            self.webcam="off"
            self.timer_label.config(text="SMILE")
            self.root.after(100, self.capture_photo)

    def capture_photo(self):
        logging.info("action: capture")
        filename = os.path.join("images", datetime.now().strftime("%d%H%M%S") + ".jpg")
        command = ["gphoto2", "--capture-image", "--filename", filename ]
        
        self.timer_label.config(text="lade ...")
        if self.live: output = self.run_command(command)
        else:
            output = "yes"
            self.run_command(["cp", "assets/corvids.jpg", filename])
        self.timer_label.config(text="")
        logging.info(output)
        if output:
            #messagebox.showinfo("Photo Captured", "Photo captured successfully.")
            self.display_last_photo(filename)

    def display_last_photo(self, filename):
        logging.info("action: display")
        # Check if the last photo exists
        self.last_picture = os.path.join(os.getcwd(), filename)
        self.start_timer_hide()
        #self.capture_button.grid(row=2, column=0, columnspan=1, sticky="ews")
        if os.path.exists(self.last_picture):
            # Load the image and display it
            image = Image.open(self.last_picture)
            # Resize image to fit window width
            window_height = self.root.winfo_height()
            image=image.crop((200, 0, image.width-200,image.height))
            image = image.resize((int(window_height*3/5*image.width/image.height), int(window_height*3/5)))
            photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=photo)
            self.photo_label.image = photo
            self.explain.config(text=self.delete_info_text)
        elif self.live:
            messagebox.showwarning("Warning", f"No photo available: {self.last_picture}")

    def delete_last(self):
        if self.status=="save":
            if self.live and os.path.exists(self.last_picture): 
                os.remove(self.last_picture)
            logging.info(f"delete {self.last_picture}")
            self.clear_all()

    def start_timer_hide(self):
        self.setstatus("save")
        self.capture_button.config(text="speichern und\n"+self.capture_text)
        self.delete_button.config(state="enable")
        self.timer_count_hide = self.config["delete_countdown"]  # 20 seconds countdown
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
            lpg = self.last_picture.replace("/images/", "/gallery/")
            os.rename(self.last_picture, lpg)
            p = multiprocessing.Process(target=to_website, args=(self.config, lpg))
            p.start()
        self.clear_all()
    
    def clear_all(self):
        logging.info("action: clear")
        self.timer_count_hide=-1
        self.timer_label.config(text="")
        self.photo_label.config(image=None)
        self.photo_label.image = None
        self.delete_button.config(state="disable")
        self.capture_button.config(text=self.capture_text)
        self.explain.config(text=self.info_text)
        self.setstatus("")
        self.last_picture=None
        if (self.webcam!="on"):
            self.photo_label.after(50,self.start_webcam)

    def start_webcam(self):
        # Set the width and height
        margin_x, margin_y = self.config["preview"]["margin_x"], self.config["preview"]["margin_y"]
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.root.winfo_width()*3/5+margin_x) 
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.root.winfo_width()*3/5*6/8+margin_y) 
        self.webcam="on"
        self.show_webcam()

    def show_webcam(self): 
        # Capture the video frame by frame 
        _, frame = self.vid.read() 
        # Convert image from one color space to other 
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        # height, width, _ = frame.shape
        # zoom_factor=self.config["preview"]["crop"]
        # crop_factor=self.config["preview"]["side_crop"]
        # margin_x = int(width * (crop_factor + (1-crop_factor) * zoom_factor))
        # margin_y = int(height * zoom_factor)
        margin_x, margin_y = self.config["preview"]["margin_x"], self.config["preview"]["margin_y"]
        cropped_image = opencv_image[margin_y:-margin_y, margin_x:-margin_x]
        # Capture the latest frame and transform to image 
        captured_image = Image.fromarray(cropped_image) 
        # Convert captured image to photoimage 
        photo_image = ImageTk.PhotoImage(image=captured_image) 
        # Displaying photoimage in the label 
        self.photo_label.photo_image = photo_image 
        # Configure image in the label 
        self.photo_label.configure(image=photo_image) 
        # Repeat the same process after every 10 seconds 
        if (self.status=="" or self.status=="timer"):
            self.photo_label.after(50, self.show_webcam) 
        # https://www.geeksforgeeks.org/how-to-show-webcam-in-tkinter-window-python/


    def exit_app(self):
        self.status="exit"
        self.root.quit()

    def setstatus(self, status):
        logging.info("status: " + status)
        self.status=status


if __name__ == "__main__":
    root = tk.Tk()
    live = True
    if (len(sys.argv)>1): live = sys.argv[1]=="live"
    app = GPhoto2GUI(root, live)
    root.mainloop()
