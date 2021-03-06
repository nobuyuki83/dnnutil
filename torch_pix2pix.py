'''
https://github.com/GINK03/pytorch-pix2pix
'''

import torch
import torch.nn as nn
from torch.autograd import Variable
import numpy as np


def weights_init(m):
  classname = m.__class__.__name__
  if classname.find('Conv') != -1:
    m.weight.data.normal_(0.0, 0.02)
  elif classname.find('BatchNorm2d') != -1 or classname.find('InstanceNorm2d') != -1:
    m.weight.data.normal_(1.0, 0.02)
    m.bias.data.fill_(0)


def get_norm_layer(norm_type):
  if norm_type == 'batch':
    norm_layer = nn.BatchNorm2d
  elif norm_type == 'instance':
    norm_layer = nn.InstanceNorm2d
  else:
    print('normalization layer [%s] is not found' % norm_type)
    norm_layer = None
  return norm_layer


def define_G(input_nc, output_nc, ngf,
             norm='batch', use_dropout=False, gpu_ids=[]):
  use_gpu = len(gpu_ids) > 0
  norm_layer = get_norm_layer(norm_type=norm)

  if use_gpu:
    assert torch.cuda.is_available()

  netG = ResnetGenerator(input_nc, output_nc, ngf,
                         norm_layer=norm_layer,
                         use_dropout=use_dropout,
                         n_blocks=9,
                         gpu_ids=gpu_ids)

  if len(gpu_ids) > 0:
    netG.cuda()

  netG.apply(weights_init)
  return netG


def define_D(input_nc, ndf,
             norm='batch', use_sigmoid=False, gpu_ids=[]):
  use_gpu = len(gpu_ids) > 0
  norm_layer = get_norm_layer(norm_type=norm)

  if use_gpu:
    assert (torch.cuda.is_available())

  netD = NLayerDiscriminator(input_nc, ndf,
                             n_layers=3,
                             norm_layer=norm_layer,
                             use_sigmoid=use_sigmoid,
                             gpu_ids=gpu_ids)

  if use_gpu:
    netD.cuda()

  netD.apply(weights_init)

  return netD


def print_network(net):
  num_params = 0
  for param in net.parameters():
    num_params += param.numel()
  print(net)
  print('Total number of parameters: %d' % num_params)


# Defines the GAN loss which uses either LSGAN or the regular GAN.
class GANLoss(nn.Module):
  def __init__(self, use_lsgan=True, target_real_label=1.0, target_fake_label=0.0,
               tensor=torch.FloatTensor):
    super(GANLoss, self).__init__()
    self.real_label = target_real_label
    self.fake_label = target_fake_label
    self.real_label_var = None
    self.fake_label_var = None
    self.Tensor = tensor
    if use_lsgan:
      self.loss = nn.MSELoss()
    else:
      self.loss = nn.BCELoss()

  def get_target_tensor(self, input:torch.Tensor, target_is_real:bool):
    target_tensor = None
    if target_is_real:
      create_label = ((self.real_label_var is None) or
                      (self.real_label_var.numel() != input.numel()))
      if create_label:
        real_tensor = self.Tensor(input.size()).fill_(self.real_label)
        self.real_label_var = Variable(real_tensor, requires_grad=False)
      target_tensor = self.real_label_var
    else:
      create_label = ((self.fake_label_var is None) or
                      (self.fake_label_var.numel() != input.numel()))
      if create_label:
        fake_tensor = self.Tensor(input.size()).fill_(self.fake_label)
        self.fake_label_var = Variable(fake_tensor, requires_grad=False)
      target_tensor = self.fake_label_var
    return target_tensor

  def __call__(self, input, target_is_real):
    target_tensor = self.get_target_tensor(input, target_is_real)
    return self.loss(input, target_tensor)
#    return self.loss(input, target_tensor.cuda())


# Defines the generator that consists of Resnet blocks between a few
# downsampling/upsampling operations.
class ResnetGenerator(nn.Module):
  def __init__(self, input_nc, output_nc,
               ngf=64, norm_layer=nn.BatchNorm2d, use_dropout=False, n_blocks=6, gpu_ids=[]):
    assert (n_blocks >= 0)
    super(ResnetGenerator, self).__init__()
    self.input_nc = input_nc
    self.output_nc = output_nc
    self.ngf = ngf
    self.gpu_ids = gpu_ids

    model = [nn.Conv2d(input_nc, ngf, kernel_size=7, padding=3),
             norm_layer(ngf, affine=True),
             nn.ReLU(True)]

    n_downsampling = 2
    for i in range(n_downsampling):
      mult = 2 ** i
      model += [nn.Conv2d(ngf * mult, ngf * mult * 2, kernel_size=3,
                          stride=2, padding=1),
                norm_layer(ngf * mult * 2, affine=True),
                nn.ReLU(True)]

    mult = 2 ** n_downsampling
    for i in range(n_blocks):
      model += [ResnetBlock(ngf * mult, 'zero', norm_layer=norm_layer, use_dropout=use_dropout)]

    for i in range(n_downsampling):
      mult = 2 ** (n_downsampling - i)
      model += [nn.ConvTranspose2d(ngf * mult, int(ngf * mult / 2),
                                   kernel_size=3, stride=2,
                                   padding=1, output_padding=1),
                norm_layer(int(ngf * mult / 2), affine=True),
                nn.ReLU(True)]

    model += [nn.Conv2d(ngf, output_nc, kernel_size=7, padding=3)]
    model += [nn.Tanh()]

    self.model = nn.Sequential(*model)

  def forward(self, input):
    if self.gpu_ids and isinstance(input.data, torch.cuda.FloatTensor):
      return nn.parallel.data_parallel(self.model, input, self.gpu_ids)
    else:
      return self.model(input)


# Define a resnet block
class ResnetBlock(nn.Module):
  def __init__(self, dim, padding_type, norm_layer, use_dropout):
    super(ResnetBlock, self).__init__()
    self.conv_block = self.build_conv_block(dim, padding_type, norm_layer, use_dropout)

  def build_conv_block(self, dim, padding_type, norm_layer, use_dropout):
    conv_block = []
    p = 0
    assert (padding_type == 'zero')
    p = 1

    conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p),
                   norm_layer(dim, affine=True),
                   nn.ReLU(True)]
    if use_dropout:
      conv_block += [nn.Dropout(0.5)]
    conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p),
                   norm_layer(dim, affine=True)]

    return nn.Sequential(*conv_block)

  def forward(self, x):
    out = x + self.conv_block(x)
    return out


# Defines the PatchGAN discriminator.
class NLayerDiscriminator(nn.Module):
  def __init__(self, input_nc,
               ndf=64, n_layers=3, norm_layer=nn.BatchNorm2d, use_sigmoid=False, gpu_ids=[]):
    super(NLayerDiscriminator, self).__init__()
    self.gpu_ids = gpu_ids

    kw = 4
    padw = int(np.ceil((kw - 1) / 2))
    sequence = [
      nn.Conv2d(input_nc, ndf, kernel_size=kw, stride=2, padding=padw),
      nn.LeakyReLU(0.2, True)
    ]

    nf_mult = 1
#    nf_mult_prev = 1
    for n in range(1, n_layers):
      nf_mult_prev = nf_mult
      nf_mult = min(2 ** n, 8)
      sequence += [
        nn.Conv2d(ndf * nf_mult_prev, ndf * nf_mult, kernel_size=kw, stride=2,
                  padding=padw), norm_layer(ndf * nf_mult,
                                            affine=True), nn.LeakyReLU(0.2, True)
      ]

    nf_mult_prev = nf_mult
    nf_mult = min(2 ** n_layers, 8)
    sequence += [
      nn.Conv2d(ndf * nf_mult_prev, ndf * nf_mult, kernel_size=kw, stride=1,
                padding=padw), norm_layer(ndf * nf_mult,
                                          affine=True), nn.LeakyReLU(0.2, True)
    ]

    sequence += [nn.Conv2d(ndf * nf_mult, 1, kernel_size=kw, stride=1, padding=padw)]

    if use_sigmoid:
      sequence += [nn.Sigmoid()]

    self.model = nn.Sequential(*sequence)

  def forward(self, input):
    if len(self.gpu_ids) and isinstance(input.data, torch.cuda.FloatTensor):
      return nn.parallel.data_parallel(self.model, input, self.gpu_ids)
    else:
      return self.model(input)


def demo():
  input_nc = 3  # input image channels
  output_nc = 3  # output image channels
  ngf = 64  # generator filter in first convolutional layer
  ndf = 64  # discriminator filters in first convolutional layer
  param_lambda = 10  # weight on L1 term in objective

  netG = define_G(input_nc, output_nc, ngf, 'batch', False, [])
  netD = define_D(input_nc + output_nc, ndf, 'batch', False, [])
  criterionGAN = GANLoss()
  criterionL1 = nn.L1Loss()
  #  criterionMSE = nn.MSELoss()

  real_in = torch.rand((1, input_nc, 256, 256), dtype=torch.float32)
  real_ot = torch.rand((1, output_nc, 256, 256), dtype=torch.float32)
  print("shape_in",real_in.shape, "shape_out",real_ot.shape)

  fake_ot = netG(real_in)

  ############################
  # (1) Update D network: maximize log(D(x,y)) + log(1 - D(x,G(x)))
  ###########################

  # train with fake
  pred_fake = netD.forward(torch.cat((real_in, fake_ot), dim=1))
  loss_d_fake = criterionGAN(pred_fake, False)

  # train with real
  pred_real = netD.forward(torch.cat((real_in, real_ot), dim=1))
  loss_d_real = criterionGAN(pred_real, True)

  # loss of the discreminator
  loss_d = (loss_d_fake + loss_d_real) * 0.5

  print("loss_d_fake", loss_d_fake.detach().item())
  print("loss_d_real", loss_d_real.detach().item())
  print("loss_d", loss_d.detach().item())

  ############################
  # (2) Update G network: maximize log(D(x,G(x))) + L1(y,G(x))
  ##########################

  # First, G(A) should fake the discriminator
  pred_fake = netD.forward(torch.cat((real_in, fake_ot), dim=1))
  loss_g_gan = criterionGAN(pred_fake, True)

  # Second, G(A) = B
  loss_g_l1 = criterionL1(fake_ot, real_ot)
  loss_g = loss_g_gan + param_lambda * loss_g_l1

  print("loss_g_gan", loss_g_gan.detach().item())
  print("loss_g_l1", loss_g_l1.detach().item())
  print("loss_g", loss_g.detach().item())


if __name__ == "__main__":
  demo()
