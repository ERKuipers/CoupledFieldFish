'''

'''
from osgeo import gdal
from osgeo import osr
from osgeo import ogr

gdal.UseExceptions()

import math
import numpy as np

import campo
from campo.points import Points
from campo.areas import Areas
from campo.property import Property


def raster_values_to_feature(point_pset, field_pset, field_prop):

  tmp_prop = Property('emptycreatename', point_pset.uuid, point_pset.space_domain, point_pset.shapes)
  
  for pidx,coordinate in enumerate(point_pset.space_domain):
    point_x = point_pset.space_domain.xcoord[pidx]
    point_y = point_pset.space_domain.ycoord[pidx]

    point_value = np.zeros(1) # should make this also for multiple agent fields 
    #point_value = np.zeros (len(field_pset.space_domain[:,1]))
    for fidx,area in enumerate(field_pset.space_domain):

      # fidx for every field in the field phenomenon 
      nr_rows = int(area[4])
      nr_cols = int(area[5]) # 
      minX = area [0]
      minY = area [1]
      cellsize = math.fabs(area[2] - minX) / nr_rows # 0 = x, from now on: rows = x , because x, y and rows,cols (though visually very unintuive i know) 

      ix = math.floor((point_x - minX) / cellsize) # needs to be rouned down since we define it by the minimum and therefore lower border
      iy = math.floor((point_y - minY) / cellsize) # need to find a solution for when point_x/y = minX/Y
      
      # reshaped = field_prop.values() #.reshape ((nr_rows, nr_cols))
      point_value[fidx] = field_prop.values()[fidx][ix,iy] # because rows, columns = x , y 
      # maybe built try except block to try the value for the different fields and skip it if the index is not available 
    tmp_prop.values()[pidx] = point_value # could be list if there are more fields at that location

  return tmp_prop
