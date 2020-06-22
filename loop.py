import math


def pick_loop_vertex(xy1:list, loops:list):
  iloop_selected = -1
  ivtx_selected = -1
  min_len = -1.0
  for iloop, loop in enumerate(loops):
    for ivtx in range(len(loop) // 2):
      xy0 = loop[ivtx * 2 + 0], loop[ivtx * 2 + 1]
      len0 = math.sqrt((xy0[0] - xy1[0]) * (xy0[0] - xy1[0]) + (xy0[1] - xy1[1]) * (xy0[1] - xy1[1]))
      if min_len < 0 or len0 < min_len:
        min_len = len0
        iloop_selected = iloop
        ivtx_selected = ivtx
  return iloop_selected,ivtx_selected


def pick_loop_edge(xy2:list, loops:list):
  iloop_selected = -1
  ivtx_selected = -1
  min_len = -1.0
  min_xy3 = [0,0]
  for iloop, loop in enumerate(loops):
    for iv0 in range(len(loop) // 2):
      iv1 = (iv0+1)%(len(loop)//2)
      xy0 = loop[iv0 * 2 + 0], loop[iv0 * 2 + 1]
      xy1 = loop[iv1 * 2 + 0], loop[iv1 * 2 + 1]
      v01 = xy1[0]-xy0[0],xy1[1]-xy0[1]
      v02 = xy2[0]-xy0[0],xy2[1]-xy0[1]
      if v01[0]*v01[0]+v01[1]*v01[1] == 0:
        continue
      ratio_selected = (v01[0]*v02[0]+v01[1]*v02[1])/(v01[0]*v01[0]+v01[1]*v01[1])
      if ratio_selected < 0.2: ratio_selected = 0.2
      if ratio_selected > 0.8: ratio_selected = 0.8
      xy3 = (1-ratio_selected)*xy0[0]+ratio_selected*xy1[0],(1-ratio_selected)*xy0[1]+ratio_selected*xy1[1]
      len23 = math.sqrt((xy2[0] - xy3[0]) * (xy2[0] - xy3[0]) + (xy2[1] - xy3[1]) * (xy2[1] - xy3[1]))
      if min_len < 0 or len23 < min_len:
        min_len = len23
        min_xy3 = xy3
        iloop_selected = iloop
        ivtx_selected = iv1
  return iloop_selected,ivtx_selected,min_xy3


def area_loop(loop:list):
  nv = len(loop)//2
  area = 0.0
  for iv0 in range(nv):
    iv1 = (iv0+1)%nv
    xy0 = loop[iv0 * 2 + 0], loop[iv0 * 2 + 1]
    xy1 = loop[iv1 * 2 + 0], loop[iv1 * 2 + 1]
    area += xy0[0]*xy1[1] - xy0[1]*xy1[0]
  return 0.5*area


def clean_loop(loops:list):
    loops_new = []
    for loop in loops:
      if len(loop) == 0:
        pass
      else:
        loops_new.append(loop)
    return loops_new


def move_segmentationloop(loops:list, iloop_selected:int, ivtx_selected:int, xy:list):
  if iloop_selected >= 0 and iloop_selected < len(loops):
    loop = loops[iloop_selected]
    if ivtx_selected >= 0 and ivtx_selected * 2 < len(loop):
      loop[ivtx_selected * 2 + 0] = xy[0]
      loop[ivtx_selected * 2 + 1] = xy[1]


def add_point_segmentation_loops(loops:list, xy1:list):
  iloop = len(loops) - 1
  loops[iloop].extend([int(xy1[0]), int(xy1[1])])