import random
import torch

class Batchloader():
  def __init__(self,
               ptIn: torch.Tensor,
               ptTg: torch.Tensor,
               batchsize=16):
    assert ptIn.shape[1] == 3
    assert ptIn.shape[0] == ptTg.shape[0]
    assert ptIn.shape[2] == ptTg.shape[1]
    assert ptIn.shape[3] == ptTg.shape[2]
    self.ptIn = ptIn
    self.ptTg = ptTg
    n = ptIn.shape[0]
    self.order = list(range(n))
    self.batchsize = batchsize
    self.ibatch = 0
    self.iepoch = 0
    random.shuffle(self.order)

  def next(self):
    n = self.ptIn.shape[0]
    i0 = (self.ibatch+0)*self.batchsize
    i1 = (self.ibatch+1)*self.batchsize
    if i1 <= n:
      ind = self.order[i0:i1]
      self.ibatch += 1
    else:
      ind = self.order[i0:n]
      self.ibatch = 0
      self.iepoch += 1
      random.shuffle(self.order)
    return self.ptIn[ind], self.ptTg[ind]


