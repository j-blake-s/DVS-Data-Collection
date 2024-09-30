import os 
import numpy as np
import torch
import torch.nn as nn


def prep_data(data_dir,save_dir):

  # Get Files
  dirs = os.listdir(data_dir)



  # Get Data Shape
  B = len(dirs)
  with np.load(os.path.join(data_dir,dirs[0])) as data:
    x = data['x']
    C, H, W, T = x.shape


  # Set up Data
  xs = np.zeros(shape=(B, C, H, W, T))
  ys = np.zeros(shape=(B,))


  # Load Data
  for i, fn in enumerate(dirs):
    with np.load(os.path.join(data_dir,fn)) as data:
      xs[i] = data['x']
      ys[i] = data['y']
  
    
  # Max Pool
  torch_xs = torch.from_numpy(xs)
  max_pool = nn.MaxPool3d((2,2,2), (2,2,2))
  torch_xs = max_pool(torch_xs)
  xs = torch_xs.numpy()
  H = H // 2
  W = W // 2
  T = T // 2


  # Flip Channels
  samples = np.zeros(shape=(B*2, C, H, W, T))
  labels = np.zeros(shape=(B*2,))

  samples[:B] = xs
  samples[B:,0,:,:,:] = xs[:,1,:,:,:]
  samples[B:,1,:,:,:] = xs[:,0,:,:,:]

  labels[:B] = ys
  labels[B:] = ys
  B = B*2

  # Shuffle
  seed = np.random.get_state()
  np.random.shuffle(samples)
  np.random.set_state(seed)
  np.random.shuffle(labels)


  # Train Test Split
  split = int(B * 0.8)

  trainX = samples[:split]
  trainY = labels[:split]

  testX = samples[split:]
  testY = labels[split:]

  # Save
  np.savez_compressed(save_dir, tX=trainX, tY=trainY, vX=testX, vY=testY)

prep_data("data", "ASL-Signs.npz")