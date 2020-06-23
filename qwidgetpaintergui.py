import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, \
  QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, \
  QSlider, QRadioButton, QButtonGroup, \
  QScrollArea
from PyQt5.QtGui import QPainter, QColor, QImage
from PyQt5.QtCore import Qt
import numpy as np
import qwidgetpainter

class QWidgetPainterGui(QWidget):
  def __init__(self, qimg_b,qimg_f,alabel):
    super(QWidgetPainterGui, self).__init__()

    scrollArea = QScrollArea()
    self.painter = qwidgetpainter.QWidgetPainter(qimg_b,qimg_f)
    self.painter.setFixedSize(qimg_b.width(),qimg_b.height())
    scrollArea.setWidget(self.painter)

    self.is_save_after_closed = False

    width0 = 200
    buttonA = QPushButton('Save && Exit')
    buttonA.setFixedWidth(width0)
    buttonA.pressed.connect(self.buttonA_pressed)

    labelA = QLabel('Alpha')
    labelA.setFixedWidth(width0)

    self.sliderA = QSlider(orientation=Qt.Horizontal)
    self.sliderA.setFixedWidth(width0)
    self.sliderA.setMaximum(255)
    self.sliderA.valueChanged.connect(self.sliderA_valueChanged)

    labelB = QLabel('Brush Size')
    labelB.setFixedWidth(width0)

    self.sliderB = QSlider(orientation=Qt.Horizontal)
    self.sliderB.setFixedWidth(width0)
    self.sliderB.setMaximum(100)
    self.sliderB.valueChanged.connect(self.sliderB_valueChanged)

    buttongroup = QButtonGroup()
    self.list_radiobutton_color = []
    for ilabel, label in enumerate(alabel):
      button = QRadioButton(label[0])
      self.list_radiobutton_color.append( (button,label[1]) )
      button.released.connect(self.buttongroup_buttonClicked)
      buttongroup.addButton(button,ilabel)
    assert len(self.list_radiobutton_color) > 0
    self.list_radiobutton_color[0][0].setChecked(True)
    self.buttongroup_buttonClicked()

    v_box = QVBoxLayout()
    v_box.addWidget(buttonA)
    v_box.addWidget(labelA)
    v_box.addWidget(self.sliderA)
    v_box.addWidget(labelB)
    v_box.addWidget(self.sliderB)
    g_box = QGridLayout()
    for i, radiobutton_color in enumerate(self.list_radiobutton_color):
      label0 = QLabel()
      label0.setText(radiobutton_color[1].name())
      label0.setFixedWidth(60)
      label1 = QLabel()
      label1.setFixedWidth(10)
      label1.setStyleSheet("background-color:"+radiobutton_color[1].name()+";")
      g_box.addWidget(radiobutton_color[0],i,0)
      g_box.addWidget(label0,i,1)
      g_box.addWidget(label1,i,2)
    v_box.addLayout(g_box)
    v_box.addStretch()

    h_box = QHBoxLayout()
    h_box.addLayout(v_box)
    h_box.addWidget(scrollArea)
    self.setLayout(h_box)

    self.update_gui_component_params()

  def sliderA_valueChanged(self,val):
    self.painter.alpha = val
    self.painter.update()
    self.update()

  def sliderB_valueChanged(self,val):
    self.painter.brushsize = val
    self.update()

  def buttongroup_buttonClicked(self):
    for radiobutton_color in self.list_radiobutton_color:
      if not radiobutton_color[0].isChecked():
        continue
      self.painter.brushcolor = radiobutton_color[1]

  def update_gui_component_params(self):
    self.sliderA.setValue( self.painter.alpha )
    self.sliderB.setValue( self.painter.brushsize )

  def buttonA_pressed(self):
    self.is_save_after_closed = True
    self.close()

if __name__ == '__main__':
  from PIL import Image

  path_img_b = "testdata/img1.jpg"
  img_b = Image.open(path_img_b)
  img_b = np.asarray(img_b).copy()
  qimage_b = QImage(img_b.data,
                    img_b.shape[1], img_b.shape[0],
                    img_b.shape[1] * 3,
                    QImage.Format_RGB888)

  path_img_f = "testdata/img1_.png"
#  img_f = Image.new('RGBA', (img_b.shape[1], img_b.shape[0]), (0, 0, 0, 0))
  img_f = Image.open(path_img_f)
  img_f = np.asanyarray(img_f).copy()
  img_f = img_f[:,:,[2,1,0,3]].copy()
  qimage_f = QImage(img_f.data,
                    img_f.shape[1], img_f.shape[0],
                    img_f.shape[1] * 4,
                    QImage.Format_ARGB32)

  alabel = []
  alabel.append(['background',QColor(0,0,0,0)])
  alabel.append(['body',QColor(255,0,0,255)])

  app = QApplication(sys.argv)
  ex = QWidgetPainterGui(qimage_b, qimage_f, alabel)
  ex.setMinimumSize(800,600)

  ex.show()
  app.exec_()

  if ex.is_save_after_closed:
    ex.painter.pixmap_f.save(path_img_f)