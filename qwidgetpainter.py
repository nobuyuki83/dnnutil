import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QRect
import numpy as np

class QWidgetPainter(QWidget):

  def __init__(self, qimage_b, qimage_f):
    super(QWidgetPainter, self).__init__()
    self.pixmap_b = QPixmap.fromImage(qimage_b)
    self.pixmap_f = QPixmap.fromImage(qimage_f)
    self.alpha = 128
    self.brushsize = 30
    self.brushcolor = QColor(255,0,0,255)

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

  def mouseMoveEvent(self, a0: QMouseEvent):
    painter_f = QPainter(self.pixmap_f)
    painter_f.setCompositionMode(QPainter.CompositionMode_Source)
    painter_f.setPen(Qt.NoPen)
#    painter_f.setBrush(QColor(255,0,0,255))
    painter_f.setBrush(self.brushcolor)
    painter_f.drawEllipse(QRect(a0.x() - self.brushsize * 0.5,
                                a0.y() - self.brushsize * 0.5,
                                self.brushsize,
                                self.brushsize))
    self.update()


if __name__ == '__main__':
  from PIL import Image

  path_img = "testdata/img1.jpg"
  img_b = Image.open(path_img)
  img_b = np.asarray(img_b).copy()
  qimage_b = QImage(img_b.data,
                    img_b.shape[1], img_b.shape[0],
                    img_b.shape[1] * 3,
                    QImage.Format_RGB888)

  img_f = Image.new('RGBA', (img_b.shape[1], img_b.shape[0]), (0, 0, 0, 0))
  img_f = np.asanyarray(img_f).copy()
  qimage_f = QImage(img_f.data,
                    img_f.shape[1], img_f.shape[0],
                    img_f.shape[1] * 4,
                    QImage.Format_ARGB32)

  painter = QPainter(qimage_f)
  painter.setPen(Qt.NoPen)
  painter.setBrush(QColor(255, 0, 0, 255))
  painter.drawRect(200, 200, 100, 100)

  app = QApplication(sys.argv)
  ex = QWidgetPainter(qimage_b, qimage_f)
  ex.show()
  app.exec_()

#  ex.pixmap_f.save("hoge.png")
#  print("hoge")