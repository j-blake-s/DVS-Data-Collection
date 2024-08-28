import cv2
import numpy as np
import argparse

def open_cam():
  print("opening camera...",end="")
  cam = cv2.VideoCapture(0)
  ret, frame = cam.read()
  
  if ret: 
    print("check")
    return cam
  else: 
    print("fail")
    quit()


def dvs(pre, cur, base,
        decay=0.3, t=0.05,
        light=(162, 249, 84), 
        dark=(255, 139, 237)):

  diff = np.mean(cur - pre, axis=-1)

  diff = np.where( np.abs(diff) < t, 0, diff)
  
  ret = np.zeros_like(cur)
  ret[diff > 0, :] = (2,2,2)
  ret[diff < 0, :] = (-2,-2,-2)

  base = (base*decay) + ret

  base[base > 1] = 1
  base[base < -1] = -1

  # print(np.unique(base))
  color = np.where(base > 0, base*light/255., base*dark/-255.)

  return base, color

def checkKey(key='q'):
  if cv2.waitKey(1) & 0xFF == ord(key):
    return True
  else: return False



def main(args):

  # Open Camera
  cam = open_cam()

  # Set up frames
  _, frame = cam.read()
  prev = np.ones_like(frame) * frame / 255.
  base = np.zeros_like(frame)
  print("Running Pseudo-DVS Camera... (press q to quit)")

  while(True):
    _, frame = cam.read()
    frame = np.array(frame, np.float32) / 255.
    base, color = dvs(prev, frame, base,decay=args.d, t=args.t)
    
    # color = cv2.resize(color, (960, 720), interpolation=cv2.INTER_LINEAR)
    cv2.imshow("DVS", color)

    prev = frame
    if checkKey('q'): break



parser = argparse.ArgumentParser('')
parser.add_argument('-d', type=float, default=0.45)
parser.add_argument('-t', type=float, default=0.05)
args = parser.parse_args()
main(args)