import cv2
import numpy as np
import argparse
import time


def open_cam():
  print("Opening Camera...",end="")
  # HAVE CHANGE IT TO 1
  cam = cv2.VideoCapture(0)
  ret, frame = cam.read()
  # ADDED CODE
  fps = cam.get(cv2.CAP_PROP_FPS)
  print("####" + str(fps))

  # ADDED CODE
  if ret: 
    print("Complete")
    return cam, frame.shape[0], frame.shape[1], int(round(fps))
  else: 
    print("Failure")
    print("Please check camera!")
    print("Exiting...")
    quit()


def dvs(pre, cur, t=0.05,
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

def checkKey():
  return cv2.waitKey(1) & 0xFF


def settings():

  print("Hello, Welcome to the DVS Recording Toolbox!")
  # Needs to be replaced with actual labels
  label_list = {1:"l1", 2 : "l2", 3 : "l3", 4 : "l4"}
  while (True):
    num_sec = int(input("How many seconds would you like to record?\n>> "))
    print("Which of the following classes is being recorded?")
    for key, val in label_list.items() :
      print(str(key) + ") " + val)
    label_int= int(input())
    label = label_list[label_int]

    user = input(f'You would like to record {num_sec} seconds of class {label}? [y/n]\n>> ')
    if user.lower() == 'y':
      print("Values accepted!") 
      return num_sec, label
    else:
      print("Please reenter values!")


def main():

  # User Settings
  num_seconds, label = settings()

  # Open Camera
  cam, img_h, img_w, fps = open_cam()
  num_frames = num_seconds * fps
  print("FPS" + str(fps), "number of frame: " + str(num_frames))
  data = np.zeros(shape=(num_frames, 2, img_h, img_w), dtype=bool)

  # Set up frames
  print("Opening Preview [Press to (r)ecord or (q)uit. IN THE PREVIEW NOT TERMINAL]")
  _, frame = cam.read()
  prev = np.ones_like(frame) * frame / 255.
  while (True):
    _, frame = cam.read()
    frame = np.array(frame, np.float32) / 255.
    _, color = dvs(prev, frame, t=0.05)    
    cv2.imshow("Frame", color)
    prev = frame
    k = checkKey()
    if k == ord('q'): quit()
    if k == ord('r'): break

  print("Recording...           ", end="\r")
  start = time.time() 
  for i in range(num_frames):    
    _, frame = cam.read()
    frame = np.array(frame, np.float32) / 255.
    spikes, color = dvs(prev, frame, t=0.05)    
    cv2.imshow("Frame", color)
    k = checkKey()
    data[i] = spikes
    prev = frame
  end = time.time()
  print(end - start, "seconds")
  print("Recording...Complete")
  fn = input("Where would you like to save this data?")
  if fn == "": fn = "./saved_data.npz"
  
  print("Saving Data...", end="\r")
  np.savez_compressed(fn, x=data, y=np.array([label]))
  print("Saving Data...Complete          ")
  
main()