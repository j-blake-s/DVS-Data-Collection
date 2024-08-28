import cv2
import numpy as np
import argparse

def open_cam():
  print("Opening Camera...",end="")
  cam = cv2.VideoCapture(0)
  ret, frame = cam.read()
  
  if ret: 
    print("Complete")
    return cam, frame.shape[0], frame.shape[1]
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
  while (True):
    num_frames = int(input("How many frames would you like to record?\n>> "))
    label = int(input("What class label is being recorded?\n>> "))

    user = input(f'You would like to record {num_frames} frames of class {label}? [y/n]\n>> ')
    if user.lower() == 'y':
      print("Values accepted!") 
      return num_frames, label
    else:
      print("Please reenter values!")


def main():

  # User Settings
  num_frames, label = settings()

  # Open Camera
  cam, img_h, img_w = open_cam()
  data = np.zeros(shape=(num_frames, 2, img_h, img_w), dtype=bool)

  # Set up frames
  print("Opening Preview [Press to (r)ecord or (q)uit]")
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
  for i in range(num_frames):    
    _, frame = cam.read()
    frame = np.array(frame, np.float32) / 255.
    spikes, color = dvs(prev, frame, t=0.05)    
    cv2.imshow("Frame", color)
    k = checkKey()
    data[i] = spikes
    prev = frame
  print("Recording...Complete")
  fn = input("Where would you like to save this data?")
  if fn == "": fn = "./saved_data.npz"
  
  print("Saving Data...", end="\r")
  np.savez_compressed(fn, x=data, y=np.array([label]))
  print("Saving Data...Complete          ")
  
main()