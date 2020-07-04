import numpy as np

def paintloops(imgseg, loops, color):
  from cv2.cv2 import fillPoly
  npls = []
  for loop in loops:
    npl = np.asarray(loop)
    npl = npl.reshape((-1, 2))
    npls.append(npl.astype(np.int32))
  return fillPoly(imgseg, npls, (color[2], color[1], color[0], color[3]))

#########################################################

def demo():
  import cv2.cv2 as cv2

  imgseg = paintloops(cv2.imread("testdata/img1_A.png",cv2.IMREAD_UNCHANGED),
                      [[100, 100, 100, 200, 200, 200, 200, 100],
                       [300, 300, 400, 400, 300, 400]],
                      [0,255,0,255])

  cv2.imshow("imgseg",imgseg)
  cv2.waitKey(0)

if __name__ == '__main__':
  demo()


