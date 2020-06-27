import random
import cv2.cv2 as cv2
import numpy as np

def pad_img_to_fit_bbox(img, x1, x2, y1, y2):
  if len(img.shape) == 3:
    img = np.pad(img, ((np.abs(np.minimum(0, y1)), np.maximum(y2 - img.shape[0], 0)),
                       (np.abs(np.minimum(0, x1)), np.maximum(x2 - img.shape[1], 0)), (0, 0)), mode="constant")
  if len(img.shape) == 2:
    img = np.pad(img, ((np.abs(np.minimum(0, y1)), np.maximum(y2 - img.shape[0], 0)),
                       (np.abs(np.minimum(0, x1)), np.maximum(x2 - img.shape[1], 0))), mode="constant")
  y2 += np.abs(np.minimum(0, y1))
  y1 += np.abs(np.minimum(0, y1))
  x2 += np.abs(np.minimum(0, x1))
  x1 += np.abs(np.minimum(0, x1))
  return img, x1, x2, y1, y2

def imcrop(img, bbox):
  '''
  crop image with bounding box
  the bounding box can be outside the image
  '''
  x1, y1, x2, y2 = bbox
  if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
    img, x1, x2, y1, y2 = pad_img_to_fit_bbox(img, x1, x2, y1, y2)
  print(x1,x2,y1,y2)
  if len(img.shape) == 3:
    return img[y1:y2, x1:x2, :]
  if len(img.shape) == 2:
    return img[y1:y2, x1:x2]

def imscalecrop(img_bgr0, scale, center, trgsize, interpolation):
  img_bgr1 = cv2.resize(img_bgr0,
                        (int(scale*img_bgr0.shape[1]), int(scale*img_bgr0.shape[0])),
                        interpolation=interpolation)
  bbox = [int(scale * center[0]-trgsize[0]*0.5),
          int(scale * center[1]-trgsize[1]*0.5),
          int(scale * center[0]-trgsize[0]*0.5)+trgsize[0],
          int(scale * center[1]-trgsize[1]*0.5)+trgsize[1]]

  img_bgr2 = imcrop(img_bgr1.copy(),bbox)
  return img_bgr2

def mask_center(imgsegbgr):
  imgsegmsk = imgsegbgr[:, :, 3] != 0
  mu = cv2.moments(imgsegmsk.reshape(*imgsegmsk.shape, 1).astype(np.float32), True)
  return int(mu["m10"] / mu["m00"]), int(mu["m01"] / mu["m00"])

def make_image_label(imgbgrseg,aColorClass):
  nplabel = np.zeros((imgbgrseg.shape[0], imgbgrseg.shape[1]), np.int32)
  for icolor, color in enumerate(aColorClass):
    if icolor == 0:
      continue
    msk = (imgbgrseg[:,:,3] == color[3])
    msk = msk & (imgbgrseg[:,:,0] == color[2])
    msk = msk & (imgbgrseg[:,:,1] == color[1])
    msk = msk & (imgbgrseg[:,:,2] == color[0])
    nplabel[msk] = icolor
  return nplabel


if __name__ == "__main__":
  path_img = "testdata/img1.jpg"
  path_imgseg = path_img.rsplit(".", 1)[0] + "_.png"
  radhead = 50

  imgsegbgr = cv2.imread(path_imgseg, cv2.IMREAD_UNCHANGED)
  cnt0 = mask_center(imgsegbgr)
  scale0 = random.uniform(20.0, 20.0) / radhead
  trgsize0 = (256, 256)

  imgbgr = imscalecrop(cv2.imread(path_img),
                       scale=scale0,
                       center=cnt0,
                       trgsize=trgsize0,
                       interpolation=cv2.INTER_CUBIC)

  imgsegbgr = imscalecrop(imgsegbgr,
                          scale=scale0,
                          center=cnt0,
                          trgsize=trgsize0,
                          interpolation=cv2.INTER_NEAREST)
  aColorClass = [
    [0, 0, 0, 0],
    [255,0,0,255] ]

  nplabel = make_image_label(imgsegbgr, aColorClass)

  cv2.imshow("hoge", imgbgr)
  cv2.imshow("hoge_lbl", nplabel.reshape(*nplabel.shape,1).astype(np.uint8)*255 )
  cv2.imshow("hoge_seg", imgsegbgr)
  cv2.waitKey(0)