import cv2
import numpy as np
import argparse
import time
import tkinter as tk
from PIL import ImageTk, Image
import threading





class GUI:
  root : tk.Tk 
  text_label : tk.Label
  text_entry : tk.Entry
  response_counter : int
  question_list = []
  response_list = []
  frame : tk.Label

  def __init__(self):
    self.question_list = ["How many seconds would you like to record?", "Which of the following classes is being recorded?", "What is your name?"]
    self.counter = 0
    pass
  def run(self):

    self.root = tk.Tk()
    self.root.title = "DVS Data Collection"

    self.text_label = tk.Label(master = self.root, text = "Hello, Welcome to the DVS Recording Toolbox!\n Click Submit to start")
    self.text_label.pack() 
    self.entry = tk.Entry(master = self.root)
    self.entry.pack()
    save_button = tk.Button(text = "Submit", command = lambda : self.next_prompt(self.counter))
    save_button.pack()
    # Create a 100x100 white image
    pil_image = Image.new('RGB', (520, 960), color='black')
    dummy_image = ImageTk.PhotoImage(pil_image)

    self.frame = tk.Label(self.root, image = dummy_image)

    self.frame.pack()

    self.root.geometry("1000x1000")
    self.root.mainloop()

  def update_frame(self, image):
    # print("INSDIE GUI LOOP")
    if (image is None):
      return
    # print(type(image))
    # print(np.shape(image))
    # cv2.imshow("name", image)
    try:
      pass
      print(np.shape(image[::2,::2,:]))
      # img = Image.fromarray(image[::2,::2], 'RGB')

      img = Image.fromarray(image, 'RGB')
      img_tk = ImageTk.PhotoImage(image = img)
      self.frame.config(image = img_tk)
      self.frame.image = img_tk
    except:
      print("INVALID")

  # def update_loop(self):
  #   while(True):
  #     self.update_frame()

  def next_prompt(self, idx):
    print(self.entry.get())
    # user_response = self.entry.get()
    self.counter += 1
    self.response_list.append(self.entry.get())
    self.text_label.config(text = (self.question_list[idx] if len(self.question_list) > idx else ""))
    





class Camera :

  num_sec : int = 10
  label : str = "l1"
  curr_frame = None
  def __init__(self):
    self.gui = GUI()
    pass


  # def run(self):
  #   thread1 = threading.Thread(target = self.camera_collection())
  #   thread1.start()
  #   # self.gui.run()
  #   # self.camera_collection()
  #   pass

  def open_cam(self):
    print("Opening Camera...",end="")
    # HAVE CHANGE IT TO 1
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

  # def checkKey(self):
  #   return cv2.waitKey(1) & 0xFF

  # def settings(self):

  #   print("Hello, Welcome to the DVS Recording Toolbox!")
  #   # Needs to be replaced with actual labels
  #   label_list = {1:"l1", 2 : "l2", 3 : "l3", 4 : "l4"}
  #   while (True):
  #     num_sec = int(input("How many seconds would you like to record?\n>> "))
  #     print("Which of the following classes is being recorded?")
  #     for key, val in label_list.items() :
  #       print(str(key) + ") " + val)
  #     label_int= int(input())
  #     label = label_list[label_int]

  #     user = input(f'You would like to record {num_sec} seconds of class {label}? [y/n]\n>> ')
  #     if user.lower() == 'y':
  #       print("Values accepted!") 
  #       return num_sec, label
  #     else:
  #       print("Please reenter values!")

    

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
    prev = np.ones_like(frame) * frame / 255.
    while (True):
      # print("INSIDE THE CAMERA LOOP")
      _, frame = cam.read()
      print(np.shape(frame))
      frame = np.array(frame, np.float32) / 255.
      _, color = self.dvs(prev, frame, t=0.05)    
      # print(color)
      # print(type(color))
      self.curr_frame = color
      # TODO 
      # self.gui.update_frame(color)
      # cv2.imshow("Frame", color)
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


  def __init__(self) -> None:
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

    print("IN HERE ")
    self.gui.run()
    # self.gui.update_frame(self.camera.curr_frame)

if __name__ == "__main__":
  manager = Manager()
  manager.run()
  # manager = CameraManager()
  # manager.run()
  # gui = GUI()
  # gui.run()