import cv2
import numpy as np
import time
import tkinter as tk
from PIL import ImageTk, Image
import threading
import time
import uuid
import asyncio


class CollectionProperties:
  num_seconds = ""
  selected_label = "EMPTY_LABEL" 
  label_dict : dict
  time_dict : dict
  def __init__(self) :
    self.label_dict = {1 : "Label 1", 2 : "Label 2", 3 : "Label 3"}
    self.time_dict = {1 : "5 Seconds", 2 : "7 Seconds", 3 : "10 Seconds" ,4 : "20 Seconds"}

  def set_seconds(self, seconds):
      self.num_seconds = seconds

  def set_label(self, label):
    self.selected_label = label

  def set_property(self, input_str : str):
    if (str(input_str) in self.label_dict.values()):
    # if self.label_dict.values str(input_str):
      self.set_label(input_str)
    else:
      print("label selected" + str(input_str))
      self.set_seconds(input_str)
  def get_seconds(self):
    return int(self.num_seconds.split(" ")[0])

class GUI:
  root : tk.Tk 
  text_label : tk.Label
  response_counter : int
  question_list = []
  response_list = []
  frame : tk.Label
  label_buttons : dict[int, tk.Button]
  time_buttons : dict[int, tk.Button]
  properties : CollectionProperties
  recording : bool
  def __init__(self):
    self.label_buttons = {}
    self.time_buttons = {}
    self.question_list = ["How many seconds would you like to record?", 
                          "Which of the following classes is being recorded?", 
                          "What is your name?"]
    self.counter = 0
    self.properties = CollectionProperties()
    self.recording = False
  def run(self):

    self.root = tk.Tk()
    self.root.title = "DVS Data Collection"
    intro_label = tk.Label(master = self.root, text = "Hello, Welcome to DVS Data Collection!")
    intro_label.pack(pady = 10)
    self.top_frame = tk.Frame(master = self.root)
    self.top_frame.pack(expand=True)
    self.left_top_frame = tk.Frame(master = self.top_frame)
    self.left_top_frame.pack(side = "left", padx= 5)
    self.count_down_frame = tk.Frame(master = self.top_frame)
    self.count_down_frame.pack(side = "right", padx = 5)

    self.right_top_frame = tk.Frame(master = self.top_frame)
    self.right_top_frame.pack(anchor = tk.CENTER, side= 'right', padx=5)
    self.middle_top_frame = tk.Frame(master = self.top_frame, bg = "black") 
    self.middle_top_frame.pack(side = "right")

    self.count_down_label = tk.Label(master = self.count_down_frame, text = "", font = ("Arial", 100, "bold"))
    self.count_down_label.pack(side= 'top', padx = 20)


    for key, value in self.properties.label_dict.items():
        button = tk.Button(master = self.left_top_frame, text = value, width = 20 ,command = lambda k = key, v = value: self.label_button_action(k, v, self.label_buttons))
        button.pack()
        self.label_buttons[key] = button
        # button.grid(row = key, column = 0)
    for key, value in self.properties.time_dict.items():

        button = tk.Button(master = self.middle_top_frame, text = value, width = 20, command = lambda k = key, v = value: self.label_button_action(k, v, self.time_buttons))
        button.pack()
        self.time_buttons[key] = button
        # button.grid(row = key, column = 1)

    record_button = tk.Button(master = self.right_top_frame, anchor = tk.CENTER, text = "Record", command = self.start_recording)
    record_button.pack(side='right', anchor= tk.CENTER)

    self.frame = tk.Label(self.root, image = None)

    self.frame.pack(side = "bottom")
    self.root.grid_columnconfigure(0, weight=1)
    self.root.grid_columnconfigure(1, weight=1)

    # self.root.geometry("1000x1000")
    self.root.mainloop()



  def start_recording(self):
    start_time = time.time()
    while(time.time() - start_time < 3):
      self.count_down_label.config(text = str(round(abs(3- (time.time() - start_time)))), foreground = "red")
      self.root.update()
    # for i in range(4):
    #   self.count_down_frame.update()
      # time.sleep(1)
    self.recording = True
    print(self.recording)

  def label_button_action(self, key, value, buttons):
    curr_button = buttons[key]
    # if curr_button.cget("relief") == tk.SUNKEN
    curr_button.config(relief=tk.SUNKEN, activebackground = "lightgreen", bg = "green")
    for dict_key, button in buttons.items():
      if dict_key != key:
        button.config(relief = tk.RAISED,bg='#f0f0f0')
    print(key)
    self.properties.set_property(value)
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

  def recording_count_down(self):
    start_time = time.time()
    while(time.time() - start_time < self.properties.get_seconds()):
      self.count_down_label.config(text = str(round(abs(self.properties.get_seconds()- (time.time() - start_time)))), foreground = "green")
      self.root.update()


    





class Camera :

  num_sec : int = 10
  label : str = "l1"
  curr_frame = None
  recording : bool
  last_recording : list
  save_data : list
  def __init__(self):
    self.recording = False
    self.last_recording = []
    # self.gui = GUI()
    pass


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
    

  def camera_preview(self) :
    print("INSIDE COLLECTION")
    # User Settings
    # num_seconds, label = self.settings()

    # Open Camera
    cam, img_h, img_w, fps = self.open_cam()
    num_frames = self.num_sec * fps
    print("FPS" + str(fps), "number of frame: " + str(num_frames))
    # data = np.zeros(shape=(num_frames, 2, img_h, img_w), dtype=bool)
    # Set up frames
    # print("Opening Preview [Press to (r)ecord or (q)uit. IN THE PREVIEW NOT TERMINAL]")
    _, frame = cam.read()

    prev = np.ones_like(frame) * (frame / 255.)

    while (True):
      # print("INSIDE THE CAMERA LOOP")
      _, frame = cam.read()
      frame = np.array(frame, np.float32) / 255.
      _, color = self.dvs(prev, frame, t=0.05)    
      # shape is (480, 640, 3)
      array_uint8 = (color * 255).astype(np.uint8)
      img = Image.fromarray(array_uint8)
      self.curr_frame = img
      prev = frame
      if self.recording:
        return


  def camera_recording(self, num_sec):

    cam, img_h, img_w, fps = self.open_cam()
    num_frames = num_sec * fps
    print("FPS : " + str(fps), "number of frame: " + str(num_frames))
    self.save_data = np.zeros(shape=(num_frames, 2, img_h, img_w), dtype=bool)
    # Set up frames
    _, frame = cam.read()
    prev = np.ones_like(frame) * (frame / 255.)
    print("Recording...           ", end="\r")
    start = time.time() 
    for i in range(num_frames):    
      _, frame = cam.read()
      frame = np.array(frame, np.float32) / 255.
      spikes, color = self.dvs(prev, frame, t=0.05)    
      array_uint8 = (color * 255).astype(np.uint8)
      img = Image.fromarray(array_uint8)
      self.curr_frame = img
      self.last_recording.append(img)
      self.save_data[i] = spikes
      prev = frame
    end = time.time()
    print(end - start, "seconds")

    



  def show_recording(self):
    print("IN SHOW RECORIDNG")
    index = 0
    while(index < len(self.last_recording)):
      print(index)
      # TODO change to 1 / fps
      time.sleep( 1 / 30)
      self.curr_frame = self.last_recording[index]
      index += 1


class Manager:
  gui : GUI
  camera : Camera


  def __init__(self):
    self.gui = GUI()
    self.camera = Camera()



  def save_recording(self):
    saving_path = "./" + str(uuid.uuid1()) + str(self.gui.properties.selected_label)
    # print("Saving Data...", end="\r")
    print("IN MANAGER SAVING DATA ...")
    np.savez_compressed(saving_path, x=self.camera.save_data, y=np.array([self.gui.properties.selected_label]))


  def update_loop(self):
    while (True):
      self.gui.update_frame(self.camera.curr_frame)
      if (self.gui.recording):
        self.camera.recording = True

  def camera_managing(self):
    while(True):
      self.camera.camera_preview()
      # self.gui.recording_count_down()
      counting_thread = threading.Thread(target = self.gui.recording_count_down)
      counting_thread.start()
      self.camera.camera_recording(self.gui.properties.get_seconds())
      self.camera.show_recording()
      self.save_recording()
      print("END OF CAMERA MANAGING ...")

  def run(self): 
    thread1 = threading.Thread(target = self.camera_managing)
    thread1.start()

    thread2 = threading.Thread(target = self.update_loop)
    thread2.start()

    self.gui.run()
    # self.gui.update_frame(self.camera.curr_frame)

if __name__ == "__main__":
  manager = Manager()
  manager.run()