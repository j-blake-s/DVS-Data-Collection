import cv2
import numpy as np
import time
import tkinter as tk
from PIL import ImageTk, Image
import threading



class CollectionProperties:
  num_seconds = 0
  selected_label = "" 
  label_dict : dict
  time_dict : dict
  def __init__(self) :
    self.label_dict = {1 : "Label 1", 2 : "Label 2", 3 : "Label 3"}
    self.time_dict = {1 : "5 seconds", 2 : "7 seconds", 3 : "10 seconds" ,4 : "20 seconds"}

  def set_seconds(self, seconds):
    if seconds > 0:
      self.num_seconds = seconds

  def set_label(self, label):
    self.selected_label = label




class GUI:
  root : tk.Tk 
  text_label : tk.Label
  text_entry : tk.Entry
  response_counter : int
  question_list = []
  response_list = []
  frame : tk.Label
  label_buttons : dict[int, tk.Button]
  time_buttons : dict[int, tk.Button]
  properties : CollectionProperties
  def __init__(self):
    self.label_buttons = {}
    self.time_buttons = {}
    self.question_list = ["How many seconds would you like to record?", 
                          "Which of the following classes is being recorded?", 
                          "What is your name?"]
    self.counter = 0
    self.properties = CollectionProperties()
  def run(self):

    self.root = tk.Tk()
    self.root.title = "DVS Data Collection"

    self.text_label = tk.Label(master = self.root, height= 20, width = 100, borderwidth = 2,relief = "solid",
                               text = "Hello, Welcome to the DVS Recording Toolbox!\n\n Click Next to start")
    self.text_label.pack() 
    self.entry = tk.Entry(master = self.root)
    self.entry.pack()

    for key, value in self.properties.label_dict.items():
        button = tk.Button(text = value, command = lambda k = key: self.label_button_action(k, self.label_buttons))
        button.pack()
        self.label_buttons[key] = button
        # button.grid(row = key, column = 0)
    for key, value in self.properties.time_dict.items():

        button = tk.Button(text = value, command = lambda k = key: self.label_button_action(k, self.time_buttons))
        button.pack()
        self.time_buttons[key] = button
        # button.grid(row = key, column = 1)

    save_button = tk.Button(text = "Next", command = lambda : self.next_prompt(self.counter))
    save_button.pack()
    # Create a 100x100 white image
    pil_image = Image.new('RGB', (1080, 1920), color='black')
    dummy_image = ImageTk.PhotoImage(pil_image)

    self.frame = tk.Label(self.root, image = dummy_image)

    self.frame.pack()
    self.root.grid_columnconfigure(0, weight=1)
    self.root.grid_columnconfigure(1, weight=1)

    self.root.geometry("1000x1000")
    self.root.mainloop()


  def label_button_action(self, key, buttons):
    # print(self.label_buttons)
    print(key)
    curr_button = buttons[key]
    # if curr_button.cget("relief") == tk.SUNKEN
    curr_button.config(relief=tk.SUNKEN, activebackground = "lightgreen", bg = "green")
    for dict_key, button in buttons.items():
      if dict_key != key:
        button.config(relief = tk.RAISED,bg='#f0f0f0')
    self.properties.set_label(key)
    return 


  def update_frame(self, image):
    if (image is None):
      return

    try:
      img_tk = ImageTk.PhotoImage(image = image)
      self.frame.config(image = img_tk)
      self.frame.image = img_tk
    except:
      print("INVALID")


  def next_prompt(self, idx):
    print(self.entry.get())
    self.counter += 1
    self.response_list.append(self.entry.get())
    self.text_label.config(text = (self.question_list[idx] if len(self.question_list) > idx else ""))
    





class Camera :

  num_sec : int = 10
  label : str = "l1"
  curr_frame = None
  def __init__(self):
    self.gui = GUI()


  def open_cam(self):
    print("Opening Camera...",end="")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    # ADDED CODE
    fps = cam.get(cv2.CAP_PROP_FPS)
    print("####" + str(fps))

    if ret: 
      print("Complete")
      return cam, frame.shape[0], frame.shape[1], int(round(fps))
    else: 
      print("Failure")
      print("Please check camera!")
      print("Exiting...")
      quit()


  def dvs(self, pre, cur, t=0.05,
          light=[162, 249, 84], 
          dark=[255, 139, 237]):

    light = list(map(lambda t: t / 255., light))
    dark = list(map(lambda t: t / 255., dark))

    diff = np.mean(cur - pre, axis=-1)
    diff = np.where( np.abs(diff) < t, 0, diff)
    
    data = np.zeros(shape=(1, 2, diff.shape[0], diff.shape[1]), dtype=bool)
    data[0, 0, diff > 0] = True
    data[0, 1, diff < 0] = True

    color = np.zeros_like(cur)
    color[diff > 0, :] = light
    color[diff < 0, :] = dark


    return data, color
    

  def camera_collection(self) :
    print("INSIDE COLLECTION")
    # User Settings
    # num_seconds, label = self.settings()

    # Open Camera
    cam, img_h, img_w, fps = self.open_cam()
    num_frames = self.num_sec * fps
    print("FPS" + str(fps), "number of frame: " + str(num_frames))
    data = np.zeros(shape=(num_frames, 2, img_h, img_w), dtype=bool)
    # Set up frames
    # print("Opening Preview [Press to (r)ecord or (q)uit. IN THE PREVIEW NOT TERMINAL]")
    _, frame = cam.read()

    prev = np.ones_like(frame) * (frame / 255.)

    while (True):
      # print("INSIDE THE CAMERA LOOP")
      _, frame = cam.read()
      frame = np.array(frame, np.float32) / 255.
      _, color = self.dvs(prev, frame, t=0.05)    

      array_uint8 = (color * 255).astype(np.uint8)
      img = Image.fromarray(array_uint8)
      self.curr_frame = img
      prev = frame
      
      # k = self.checkKey()
      # if k == ord('q'): quit()
      # if k == ord('r'): break

    print("Recording...           ", end="\r")
    start = time.time() 
    for i in range(num_frames):    
      _, frame = cam.read()
      frame = np.array(frame, np.float32) / 255.
      spikes, color = self.dvs(prev, frame, t=0.05)    
      cv2.imshow("Frame", color)
      k = self.checkKey()
      data[i] = spikes
      prev = frame
    end = time.time()
    print(end - start, "seconds")
    print("Recording...Complete")
    fn = input("Where would you like to save this data?")
    if fn == "": fn = "./saved_data.npz"
    
    print("Saving Data...", end="\r")
    np.savez_compressed(fn, x=data, y=np.array([self.label]))
    print("Saving Data...Complete          ")



class Manager:
  gui : GUI
  camera : Camera


  def __init__(self):
    self.gui = GUI()
    self.camera = Camera()


  def update_loop(self):
    while (True):
      self.gui.update_frame(self.camera.curr_frame)

  def run(self): 
    thread1 = threading.Thread(target = self.camera.camera_collection)
    thread1.start()

    thread2 = threading.Thread(target = self.update_loop)
    thread2.start()

    self.gui.run()
    # self.gui.update_frame(self.camera.curr_frame)

if __name__ == "__main__":
  manager = Manager()
  manager.run()