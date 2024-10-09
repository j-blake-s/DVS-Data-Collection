import os 
import numpy as np
import torch
import torch.nn as nn
import sys

def prep_data(data_dir,save_dir):

  # Get Files
  dirs = os.listdir(data_dir)



  # Get Data Shape
  B = len(dirs)
  with np.load(os.path.join(data_dir,dirs[0])) as data:
    x = data['x']
    C, H, W, T = x.shape

  # Load Data
  for i, fn in enumerate(dirs):
    with np.load(os.path.join(data_dir,fn)) as data:
      x = data['x']
      y = data['y']
  
    
    # Max Pool
    torch_x = torch.from_numpy(x).to(torch.float32)
    max_pool = nn.MaxPool3d((2,2,2), (2,2,2))
    torch_x = max_pool(torch_x)
    x = torch_x.numpy().astype(bool)
    H = H // 2
    W = W // 2
    T = T // 2


    xc = np.zeros_like(x)

    xc[0] = x[1]
    xc[1] = x[0]


    np.savez_compressed(os.path.join(save_dir, fn), x=x, y=y)
    np.savez_compressed(os.path.join(save_dir, f'{fn[:-4]}_flip.npz'), x=xc, y=y)

# prep_data("/home/seekingj/data/ASL/raw", "/home/seekingj/data/ASL/prep")
prep_data(sys.argv[1],sys.argv[2])