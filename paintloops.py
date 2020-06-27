import os.path
import numpy as np
import cv2.cv2 as cv2

def paintloops(imgsize, path_imgseg, loops, color):

  if os.path.isfile(path_imgseg):
    imgseg = cv2.imread(path_imgseg)
    if imgseg.shape[0] != imgsize[0] or imgseg.shape[1] != imgsize[1] or imgseg.shape[2] != 4:
      imgseg = np.zeros((imgsize[1], imgsize[0], 4))
  else:
    imgseg = np.zeros((imgsize[1], imgsize[0], 4))

  npls = []
  for loop in loops:
    npl = np.asarray(loop)
    npl = npl.reshape((-1, 2))
    npls.append(npl.astype(np.int32))
  imgseg = cv2.fillPoly(imgseg, npls, (color[2], color[1], color[0], color[3]))

  return imgseg

if __name__ == '__main__':

  path_img = "testdata/img1.jpg"
  path_imgseg = path_img.rsplit(".",1)[0]+"_1_.png"
  loops = [[100,100, 100,200, 200,200, 200,100],
           [300, 300, 400, 400, 300, 400]]
  color = [255,0,0,255]

  imgseg = paintloops(cv2.imread(path_img).shape[::-1][1:3],
                      path_imgseg,
                      loops,
                      color)

  print(imgseg.shape)
  cv2.imshow("imgseg",imgseg)
  cv2.waitKey(0)

  #cv2.imwrite(path_imgseg,imgseg)


