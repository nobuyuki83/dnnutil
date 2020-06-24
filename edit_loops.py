from enum import Enum
import glfw
import OpenGL.GL as gl
import cv2, sys, os

import my_gl

def display(loops:list,iloop_selected:int,img_size_info:list):
  gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
  my_gl.set_view_trans(img_size_info)
  my_gl.draw_img(img_size_info)
  my_gl.draw_loops(loops,
                   selected_loop=iloop_selected)
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

def edit_loops(path_img:str, loops:list):
  class EditMode(Enum):
    EDIT_LOOP = 1
    NEW_LOOP = 2

  ivtx_selected = -1
  iloop_selected = -1
  is_mouse_down = False
  mode_edit = EditMode.EDIT_LOOP
  mode_exit = ExitFlag.NO_EXIT

  def mouse_button(window, button, action, mods):
    nonlocal is_mouse_down, iloop_selected, ivtx_selected
    import loop
    pos = glfw.get_cursor_pos(window)
    xy = my_gl.get_img_coord(pos, img_size_info)
    if action == glfw.PRESS:
      is_mouse_down = True
      if mode_edit.EDIT_LOOP:
        if button == glfw.MOUSE_BUTTON_LEFT:
          iloop_selected, ivtx_selected = loop.pick_loop_vertex(xy, loops)
        if button == glfw.MOUSE_BUTTON_RIGHT:
          iloop_selected, ivtx_selected, xy3 = loop.pick_loop_edge(xy, loops)
          if not ivtx_selected == -1:
            loop = loops[iloop_selected]
            loop.insert(ivtx_selected * 2 + 0, xy[0])
            loop.insert(ivtx_selected * 2 + 1, xy[1])
        if button == glfw.MOUSE_BUTTON_MIDDLE:
          iloop_selected, ivtx_selected = loop.pick_loop_vertex(xy, loops)
          if not ivtx_selected == -1:
            loop = loops[iloop_selected]
            loop.pop(ivtx_selected * 2 + 1)
            loop.pop(ivtx_selected * 2 + 0)
            ivtx_selected = -1
      if mode_edit == EditMode.NEW_LOOP:
        loop.add_point_segmentation_loops(loops, xy)
    elif action == glfw.RELEASE:
      iloop_selected = -1
      ivtx_selected = -1
      is_mouse_down = False

  def cursor_pos(window, xpos, ypos):
#    import dnnutil.loop as loop
    import loop as loop
    if not is_mouse_down:
      return
    if mode_edit == EditMode.EDIT_LOOP:
      xy = my_gl.get_img_coord((xpos,ypos), img_size_info)
      loop.move_segmentationloop(loops, iloop_selected, ivtx_selected, xy)

  def keyboard(window, key, scancode, action, mods):
    nonlocal mode_edit, iloop_selected, ivtx_selected, mode_exit
    if action != glfw.PRESS:
      return
    if key == glfw.KEY_1:
      # change edit mode to loop
      glfw.set_window_title(window,"new loop")
      mode_edit = EditMode.NEW_LOOP
      loops.append([])
      iloop_selected = 0
    elif key == glfw.KEY_2:
      glfw.set_window_title(window,"edit loop")
      mode_edit = EditMode.EDIT_LOOP
      iloop_selected = -1
      ivtx_selected = -1
    elif key == glfw.KEY_D:
      # delete selected loop
      if 0 <= iloop_selected < len(loops):
        loops.pop(iloop_selected)
        nloop = len(loops)
        if nloop == 0:
          iloop_selected = -1
        else:
          iloop_selected = (iloop_selected + nloop - 1) % nloop
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

  img_size_info = my_gl.load_texture( cv2.imread(path_img) )

  while not glfw.window_should_close(window):
    display(loops,iloop_selected,img_size_info)
    glfw.swap_buffers(window)
    glfw.poll_events()
    if mode_exit != ExitFlag.NO_EXIT:
      break

  glfw.terminate()

  return mode_exit

if __name__ == "__main__":
  loops = [[100,100, 100,200, 200,200, 200,100],
           [300, 300, 400, 400, 300, 400]]
  while True:
    mode_exit = edit_loops("testdata/img1.jpg", loops)
    print(mode_exit)
    if mode_exit == ExitFlag.EXIT_WITHOUT_SAVE or mode_exit == ExitFlag.NO_EXIT:
      break