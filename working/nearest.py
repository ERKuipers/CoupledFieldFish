import numpy as np
import random 
from pathlib import Path 
import sys
in_dir = Path.cwd()
up_dir = in_dir.parent
working = up_dir / 'working'
sys.path.append(f'{working}')
from lookup import raster_values_to_feature, zonal_values_to_feature
import campo
import math
from osgeo import gdal
from osgeo import osr
from osgeo import ogr

gdal.UseExceptions()

import math
import numpy as np
from campo import Property 

def single_feature_to_raster(field_pset, point_pset, pidx):

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(28992)

    ogr_source=ogr.GetDriverByName('MEMORY').CreateDataSource('memSource')

    tmp_prop = Property('emptycreatename', field_pset.uuid, field_pset.space_domain, field_pset.shapes)

    for fidx, area in enumerate(field_pset.space_domain):
        # Point feature for current location
        point_x = point_pset.space_domain.xcoord[pidx]
        point_y = point_pset.space_domain.ycoord[pidx]

        layername = 'locations'
        if ogr_source.GetLayerByName(layername):
            ogr_source.DeleteLayer(layername)

        lyr = ogr_source.CreateLayer(layername, geom_type=ogr.wkbPoint, srs=spatial_ref)

        feat = ogr.Feature(lyr.GetLayerDefn())
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(point_x, point_y)
        feat.SetGeometry(point)

        lyr.CreateFeature(feat)

        # Raster
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

        tmp_prop.values()[fidx] = array

    return tmp_prop


def find_nearest (point_pset, field_pset, pidx, boolean_fieldprop,zeroprop, oneprop): 
    point_fieldprop = single_feature_to_raster(field_pset, point_pset, pidx)
    spread_from_point_prop = campo.spread (point_fieldprop, zeroprop, oneprop)
    distance_to_dest_prop = campo.mul (spread_from_point_prop, boolean_fieldprop)
    return distance_to_dest_prop