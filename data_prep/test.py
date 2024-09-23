


import numpy as np
import torch
import torch.nn as nn






data = (torch.rand(size=(5, 2, 480, 640, 90)) < 0.1).to(torch.float32)
layer = nn.MaxPool3d((2,2,2), stride=(2,2,2),)

out = layer(data)


print(data.shape)
print(out.shape)