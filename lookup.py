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
  # point_value = np.zeros (len(field_pset.space_domain[:,1]))
  for pidx,coordinate in enumerate(point_pset.space_domain):
    point_x = point_pset.space_domain.xcoord[pidx]
    point_y = point_pset.space_domain.ycoord[pidx]
    print (point_x)
    print(point_y)

    
    for fidx,area in enumerate(field_pset.space_domain):
      # fidx for every field in the field phenomenon 
      nr_rows = int(area[4])
      nr_cols = int(area[5]) # 
      minX = area [0]
      minY = area [1]
      cellsize = math.fabs(area[2] - minX) / nr_rows # 0 = x, from now on: rows = x , because x, y and rows,cols (though visually very unintuive i know) 

      print (minX)
      print(minY)

      ix = math.floor((point_x - minX) / cellsize) # needs to be rouned down since we define it by the minimum and therefore lower border
      iy = math.floor((point_y - minY) / cellsize) # need to find a solution for when point_x/y = minX/Y
      
      # reshaped = field_prop.values() #.reshape ((nr_rows, nr_cols))
    
      #print (field_prop.values().values.shape)
      point_value[fidx] = field_prop[fidx].values()[ix,iy] # because rows, columns = x , y 
      # maybe built try except block to try the value for the different fields and skip it if the index is not available 
    tmp_prop.values()[pidx] = point_value # could be list if there are more fields at that location

  return tmp_prop

def feature_to_raster_all(field_pset, point_pset):

  spatial_ref = osr.SpatialReference()
  spatial_ref.ImportFromEPSG(28992)

  outdriver=ogr.GetDriverByName('MEMORY')
  source=outdriver.CreateDataSource('memData')
  tmp=outdriver.Open('memData', 1)
  lyr = source.CreateLayer('locations', geom_type=ogr.wkbPoint, srs=spatial_ref)


  for coordinate in point_pset.space_domain:
    feat = ogr.Feature(lyr.GetLayerDefn())
    feat.SetGeometry(ogr.CreateGeometryFromWkt('POINT({} {})'.format(float(coordinate[0]), float(coordinate[1]))))

    lyr.CreateFeature(feat)


  tmp_prop = Property('emptycreatename', field_pset.uuid, field_pset.space_domain, field_pset.shapes)

  for idx,area in enumerate(field_pset.space_domain):

    nr_rows = int(area[4])
    nr_cols = int(area[5])
    cellsize = cellsize = math.fabs(area[2] - area[0]) / nr_cols


    minX = area[0]
    maxY = area[3]


    target_ds = gdal.GetDriverByName('MEM').Create('', nr_cols, nr_rows, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((minX, cellsize, 0, maxY, 0, -cellsize))
    target_ds.SetProjection(spatial_ref.ExportToWkt())

    gdal.PushErrorHandler('CPLQuietErrorHandler')
    err = gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1], options=['ALL_TOUCHED=TRUE'])
    gdal.PopErrorHandler()

    band = target_ds.GetRasterBand(1)
    array = band.ReadAsArray()

    tmp_prop.values()[idx] = array


  return tmp_prop



def feature_values_to_raster(field_pset, point_pset, point_prop):

  tmp_prop = Property('emptycreatename', field_pset.uuid, field_pset.space_domain, field_pset.shapes)

  for idx,area in enumerate(field_pset.space_domain):

    nr_rows = int(area[4])
    nr_cols = int(area[5])

    raster = np.zeros((nr_rows *  nr_cols))

    for pidx,coordinate in enumerate(point_pset.space_domain):
      raster[pidx] = point_prop.values()[pidx][0]

    tmp_prop.values()[idx] = raster.reshape((nr_rows, nr_cols))

  return tmp_prop