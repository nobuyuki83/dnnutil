import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QRect, pyqtSignal
import numpy as np

class QWidgetPainter(QWidget):

  signalParamChanged = pyqtSignal()

  def __init__(self,
               npimgrgb_b: np.ndarray,
               npimgbgra_f: np.ndarray):
    super(QWidgetPainter, self).__init__()

    assert type(npimgrgb_b) == np.ndarray
    assert len(npimgrgb_b.shape) == 3
    assert npimgrgb_b.shape[2] == 3
    assert npimgrgb_b.dtype == np.uint8
    assert type(npimgbgra_f) == np.ndarray
    assert len(npimgbgra_f.shape) == 3
    assert npimgbgra_f.shape[2] == 4
    assert npimgbgra_f.dtype == np.uint8
    assert npimgrgb_b.shape[:2] == npimgbgra_f.shape[:2]

    self.pixmap_b = QPixmap.fromImage(
      QImage(npimgrgb_b.data,
             npimgrgb_b.shape[1], npimgrgb_b.shape[0],
             npimgrgb_b.shape[1] * 3,
             QImage.Format_RGB888) )
    self.pixmap_f = QPixmap.fromImage(
      QImage(npimgbgra_f.data,
             npimgbgra_f.shape[1], npimgbgra_f.shape[0],
             npimgbgra_f.shape[1] * 4,
             QImage.Format_ARGB32) )
    ###
    self.alpha = 128
    self.brushsize = 30
    self.brushcolor = QColor(255,0,0,255)
    self.brushpos = [0,0]
    self.is_paint_atop = False
    self.setMouseTracking(True)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(255,255,255,self.alpha))
    painter.drawRect(0,0,self.pixmap_f.width(),self.pixmap_f.height())
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.drawPixmap(0, 0, self.pixmap_f.width(), self.pixmap_f.height(), self.pixmap_f) # annotation
    painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
    painter.drawPixmap(0, 0, self.pixmap_b.width(), self.pixmap_b.height(), self.pixmap_b) # image
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.setPen(Qt.black)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QRect(self.brushpos[0] - self.brushsize * 0.5,
                              self.brushpos[1] - self.brushsize * 0.5,
                              self.brushsize,
                              self.brushsize) )

  def mouseMoveEvent(self, a0: QMouseEvent):
    from math import sqrt
    if a0.buttons() == Qt.LeftButton and a0.modifiers() == Qt.NoModifier:
      painter_f = QPainter(self.pixmap_f)
      if self.is_paint_atop:
        painter_f.setCompositionMode(QPainter.CompositionMode_SourceAtop)
      else:
        painter_f.setCompositionMode(QPainter.CompositionMode_Source)
      painter_f.setPen(Qt.NoPen)
      painter_f.setBrush(self.brushcolor)
      painter_f.drawEllipse(QRect(a0.x() - self.brushsize * 0.5,
                                  a0.y() - self.brushsize * 0.5,
                                  self.brushsize,
                                  self.brushsize))
      self.brushpos[0] = a0.x()
      self.brushpos[1] = a0.y()
    elif a0.buttons() == Qt.LeftButton and a0.modifiers() & Qt.ShiftModifier:
      dx = a0.x() - self.brushpos[0]
      dy = a0.y() - self.brushpos[1]
      len = sqrt(dx*dx+dy*dy)
      self.brushsize = 2*len
      self.brushsize = abs(self.brushsize)
      self.signalParamChanged.emit()
    self.update()

#################################################################
# demo from here

def demo():
  from PIL import Image, ImageDraw

  img_b = np.asarray(Image.open("testdata/img1.jpg"))

  img_f = Image.new('RGBA', (img_b.shape[1], img_b.shape[0]), (0, 0, 0, 0))
  ImageDraw.Draw(img_f).rectangle((200, 200, 300, 300), fill=(255, 0, 0, 255)) # blue
  img_f = np.asanyarray(img_f).copy()

  with QApplication(sys.argv) as app:
    # demo1
    ex = QWidgetPainter(img_b.copy(), img_f.copy())
    ex.show()
    app.exec_()

    # demo2
    ex = QWidgetPainter(img_b.copy(), img_f.copy())
    ex.is_paint_atop = True
    ex.show()
    app.exec_()

if __name__ == '__main__':
  demo()

