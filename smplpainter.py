import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QRect
import numpy as np

class ImageWidget(QWidget):

  def __init__(self, qimage_b, qimage_f):
    super(ImageWidget, self).__init__()
    self.pixmap_b = QPixmap.fromImage(qimage_b)
    self.pixmap_f = QPixmap.fromImage(qimage_f)
    painter = QPainter(self.pixmap_f)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(255,0,0,255))
    painter.drawRect(200,200,100,100)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(255,255,255,200))
    painter.drawRect(0,0,self.pixmap_f.width(),self.pixmap_f.height())
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.drawPixmap(0, 0, self.pixmap_f.width(), self.pixmap_f.height(), self.pixmap_f) # annotation
    painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
    painter.drawPixmap(0, 0, self.pixmap_b.width(), self.pixmap_b.height(), self.pixmap_b) # image

  def mouseMoveEvent(self, a0: QMouseEvent):
    painter_f = QPainter(self.pixmap_f)
    painter_f.setCompositionMode(QPainter.CompositionMode_Source)
    painter_f.setPen(Qt.NoPen)
    painter_f.setBrush(QColor(255,0,0,255))
    painter_f.drawRect(QRect(a0.x()-50, a0.y()-50, 100, 100))
    self.update()


def main():
  path_img = "downloads/aa9ccaf3769774f5397d33ab402b0f73.jpg"

  from PIL import Image
  img_b = Image.open(path_img)
#    img0 = Image.open("downloads/c6b0693763ae6b37b01d52a1ee9ea920.jpg")
  img_b = np.asarray(img_b).copy()
#    print(type(img0),img0.shape)

  img_f = Image.new('RGBA', (img_b.shape[1], img_b.shape[0]), (0, 0, 0, 0))
  img_f = np.asanyarray(img_f).copy()

  qimage_b = QImage(img_b.data,
                    img_b.shape[1], img_b.shape[0],
                    img_b.shape[1] * 3,
                    QImage.Format_RGB888)

  qimage_f = QImage(img_f.data,
                    img_f.shape[1], img_f.shape[0],
                    img_f.shape[1] * 4,
                    QImage.Format_ARGB32)

  app = QApplication(sys.argv)
  ex = ImageWidget(qimage_b,qimage_f)
  ex.show()
  app.exec_()

  ex.pixmap_f.save("hoge.png")
  print("hoge")

if __name__ == '__main__':
  main()