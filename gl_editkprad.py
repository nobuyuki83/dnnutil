from enum import Enum
import numpy as np
import math
#
import glfw
import OpenGL.GL as gl

import gl_util

def display(kprad,
            iselected: int,
            img_size_info:list):
  gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
  gl_util.set_view_trans(img_size_info)
  gl_util.draw_img(img_size_info)

  # draw circle
  if iselected == 1:
    gl_util.drawCircle((kprad[0],kprad[1]),kprad[2],color=(1,0,0))
  else:
    gl_util.drawCircle((kprad[0],kprad[1]),kprad[2],color=(1,1,1))

  # draw center point
  gl.glPointSize(5)
  if iselected == 0:
    gl.glColor3d(1,0,0)
  else:
    gl.glColor3d(1,1,1)
  gl.glBegin(gl.GL_POINTS)
  gl.glVertex2d(kprad[0],-kprad[1])
  gl.glEnd()

  gl.glDisable(gl.GL_TEXTURE_2D)
  gl.glMatrixMode(gl.GL_MODELVIEW)
  gl.glLoadIdentity()
  gl.glMatrixMode(gl.GL_PROJECTION)
  gl.glLoadIdentity()

class ExitFlag(Enum):
  NO_EXIT = 1
  EXIT_WITHOUT_SAVE = 2
  SAVE = 3
  NEXT1 = 4
  NEXT10 = 5

def edit_kprad(imgbgr:np.ndarray, kprad:list):

  iselected = -1
  is_mouse_down = False
  mode_exit = ExitFlag.NO_EXIT

  def mouse_button(window, button, action, mods):
    nonlocal is_mouse_down, iselected
    pos = glfw.get_cursor_pos(window)
    xy = gl_util.get_img_coord(pos, img_size_info)
    iselected = -1
    if action == glfw.PRESS:
      is_mouse_down = True
      if button == glfw.MOUSE_BUTTON_LEFT:
        len0 = math.sqrt( (kprad[0]-xy[0])*(kprad[0]-xy[0]) + (kprad[1]-xy[1])*(kprad[1]-xy[1]) )
        if len0 < 10:
          iselected = 0
        elif (len0-kprad[2])<10:
          iselected = 1
    elif action == glfw.RELEASE:
      is_mouse_down = False

  def cursor_pos(window, xpos, ypos):
    if not is_mouse_down:
      return
    xy = gl_util.get_img_coord((xpos,ypos), img_size_info)
    len0 = math.sqrt((kprad[0] - xy[0]) * (kprad[0] - xy[0]) + (kprad[1] - xy[1]) * (kprad[1] - xy[1]))
    if iselected == 0:
      kprad[0] = xy[0]
      kprad[1] = xy[1]
    if iselected == 1:
      kprad[2] = len0


  def keyboard(window, key, scancode, action, mods):
    nonlocal iselected, mode_exit
    if action != glfw.PRESS:
      return
    elif key == glfw.KEY_S:
      mode_exit = ExitFlag.SAVE
    elif key == glfw.KEY_Q:
      mode_exit = ExitFlag.EXIT_WITHOUT_SAVE
    elif key == glfw.KEY_RIGHT:
      mode_exit = ExitFlag.NEXT1

  if not glfw.init():
    raise RuntimeError('Could not initialize GLFW3')

  window = glfw.create_window(600, 600, 'edit_loop', None, None)
  if not window:
    glfw.terminate()
    raise RuntimeError('Could not create an window')

  glfw.make_context_current(window)
  glfw.set_cursor_pos_callback(window, cursor_pos)
  glfw.set_mouse_button_callback(window, mouse_button)
  glfw.set_key_callback(window, keyboard)

  img_size_info = gl_util.load_texture( imgbgr )

  while not glfw.window_should_close(window):
    display(kprad,iselected,img_size_info)
    glfw.swap_buffers(window)
    glfw.poll_events()
    if mode_exit != ExitFlag.NO_EXIT:
      break

  glfw.terminate()

  return mode_exit

def demo():
  import cv2.cv2 as cv2

  while True:
    kprad = [300,300,50]
    mode_exit = edit_kprad(cv2.imread("testdata/img1.jpg"),
                           kprad)
    print("output:",kprad)

    # exit without save
    if mode_exit == ExitFlag.EXIT_WITHOUT_SAVE or mode_exit == ExitFlag.NO_EXIT:
      break

if __name__ == "__main__":
  demo()
