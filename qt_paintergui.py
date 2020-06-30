import sys
import numpy as np
#
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, \
  QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, \
  QSlider, QRadioButton, QButtonGroup, \
  QScrollArea, QCheckBox
from PyQt5.QtGui import QColor, QKeyEvent
from PyQt5.QtCore import Qt
#
import qt_painter

class QWidgetPainterGui(QWidget):

  def __init__(self,
               npimgrgb_b,
               npimgbgra_f,
               alabel):
    super(QWidgetPainterGui, self).__init__()

    self.is_save_after_closed = False

    ###

    scrollArea = QScrollArea()
    self.painter = qt_painter.QWidgetPainter(npimgrgb_b, npimgbgra_f)
    self.painter.setFixedSize(npimgrgb_b.shape[1], npimgrgb_b.shape[0])
    scrollArea.setWidget(self.painter)
    self.painter.signalParamChanged.connect(self.update_gui_component_params)

    h_box = QHBoxLayout()
    h_box.addLayout(self.init_left_Layout(alabel))
    h_box.addWidget(scrollArea)
    self.setLayout(h_box)

    self.update_gui_component_params()

  def init_left_Layout(self,alabel):
    self.checkbox = QCheckBox('Paint ATop')
    self.checkbox.toggled.connect(self.checkbox_toggled)
    #####
    labelA = QLabel('Alpha')
    labelA.setFixedWidth(80)
    self.sliderA = QSlider(orientation=Qt.Horizontal)
    self.sliderA.setFixedWidth(120)
    self.sliderA.setMaximum(255)
    self.sliderA.valueChanged.connect(self.sliderA_valueChanged)
    #####
    labelB = QLabel('Brush Size')
    labelB.setFixedWidth(80)
    self.sliderB = QSlider(orientation=Qt.Horizontal)
    self.sliderB.setFixedWidth(120)
    self.sliderB.setMaximum(255)
    self.sliderB.valueChanged.connect(self.sliderB_valueChanged)
    #####
    g_boxA = QGridLayout()
    g_boxA.addWidget(labelA,0,0)
    g_boxA.addWidget(self.sliderA,0,1)
    g_boxA.addWidget(labelB,1,0)
    g_boxA.addWidget(self.sliderB,1,1)
    #####
    self.buttongroup = QButtonGroup()
    self.list_radiobutton_color = []
    for ilabel, label in enumerate(alabel):
      radiobutton = QRadioButton(label[0])
      self.list_radiobutton_color.append( (radiobutton,label[1]) )
      radiobutton.released.connect(self.buttongroup_buttonClicked)
      self.buttongroup.addButton(radiobutton,ilabel)
    assert len(self.list_radiobutton_color) > 0
    self.list_radiobutton_color[0][0].setChecked(True)
    self.buttongroup_buttonClicked()
    #####
    v_box = QVBoxLayout()
    v_box.addWidget(self.checkbox)
    v_box.addSpacing(20)
    v_box.addLayout(g_boxA)
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
    return v_box

  def keyPressEvent(self, a0: QKeyEvent) -> None:
    if a0.text() == "f":
      buttons = self.buttongroup.buttons()
      id = self.buttongroup.checkedId()
      buttons[(id+1)%len(buttons)].setChecked(True)
      self.buttongroup_buttonClicked()
    if a0.text() == 'g':
      self.checkbox.toggle()
      self.painter.is_paint_atop = self.checkbox.isChecked()
    if a0.text() == "s":
      self.is_save_after_closed = True
      self.close()
    if a0.text() == "q":
      self.is_save_after_closed = False
      self.close()

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

  def checkbox_toggled(self,isChecked:bool):
    self.painter.is_paint_atop = isChecked



def painter_gui(npimgrgb_b:np.ndarray,
                npimgrgba_f:np.ndarray,
                alabel:list):
  '''
  :param npimgrgb_b: numpy.ndarray rgb wihtout alpha channel
  :param npimgrgba_f: numpy.ndarray rgba
  :param alabel:
  :return:
  '''
  assert npimgrgb_b.shape[2] == 3 and npimgrgba_f.shape[2] == 4
  assert npimgrgb_b.shape[:2] == npimgrgba_f.shape[:2]
  assert len(npimgrgba_f.shape) == len(npimgrgb_b.shape) == 3
  assert npimgrgb_b.dtype == npimgrgba_f.dtype == np.uint8

  aNameColor = []
  for label in alabel:
    aNameColor.append([label[0], QColor(*label[1])])

  with QApplication(sys.argv) as app:
    ex = QWidgetPainterGui(npimgrgb_b,
                           npimgrgba_f[:, :, [2, 1, 0, 3]].copy(), # rgba -> bgra
                           aNameColor)
    ex.setMinimumSize(800, 600)
    ex.show()
    app.exec_()

  qimage_fo = ex.painter.pixmap_f.toImage()
  ptr = qimage_fo.bits()
  ptr.setsize(qimage_fo.height()*qimage_fo.width()*4)
  npimg_fo = np.array(ptr).reshape((qimage_fo.height(), qimage_fo.width(), 4))[:,:,[2,1,0,3]]

  return npimg_fo, ex.is_save_after_closed

############################################

def demo():
  from PIL import Image

  np_imgseg, is_save = painter_gui(
    np.asarray(Image.open("testdata/img1.jpg")).copy(),
    np.asarray(Image.open("testdata/img1_A.png")).copy(),
    alabel = [
      ['background', (0, 0, 0, 0)],
      ['body', (255, 0, 0, 255)],
      ['face', (0, 0, 255, 255)]] )

  Image.fromarray(np_imgseg).show()

if __name__ == '__main__':
  demo()