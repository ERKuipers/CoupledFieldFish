import campo
import math
import os
import subprocess
import tempfile
import shutil

from osgeo import gdal, osr
import pandas as pd
from campo.dataframe import *
from campo.utils import _color_message

gdal.UseExceptions()

def _gdal_datatype(data_type):
    """ return corresponding GDAL datatype """

    if data_type == 'bool':
        return gdal.GDT_Byte
    elif data_type == 'int32':
        return gdal.GDT_Int32
    elif data_type == 'int64':
        return gdal.GDT_Int64
    elif data_type == 'float32':
        return gdal.GDT_Float32
    elif data_type == 'float64':
        return gdal.GDT_Float64
    else:
        raise ValueError(f"Data type '{data_type}' non-suported")


def to_geotiff(dataframe, path: str, crs: str) -> None:
    """ Exports field agent property to a GeoTIFF

    :param dataframe: Input dataframe from LUE dataset for particular timestep
    :param path: Output path
    :param crs: Coordinate Reference System, e.g. "EPSG:4326"
    """

    if crs != "":
        aut, code = crs.split(":")
        if aut != "EPSG":
            msg = _color_message('Provide CRS like "EPSG:4326"')
            raise TypeError(msg)

    rows = dataframe.values.shape[0]
    cols = dataframe.values.shape[1]
    cellsize_x = math.fabs(dataframe.xcoord[1].values - dataframe.xcoord[0].values)
    cellsize_y = math.fabs(dataframe.ycoord[1].values - dataframe.ycoord[0].values)

    data = dataframe.data

    xmin = dataframe.xcoord[0].values.item()
    # last ycoordinate is the lower of the topmost row, we need the upper ycoordinate for the extent
    ymax = dataframe.ycoord[-1].values.item() + cellsize_y
    geotransform = (xmin, cellsize_x, 0, ymax, 0, -cellsize_y)

    out_ds = gdal.GetDriverByName('GTiff').Create(str(path), rows, cols, 1, _gdal_datatype(data.dtype))
    out_ds.SetGeoTransform(geotransform)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(int(code))
    out_ds.SetProjection(srs.ExportToWkt())

    out_ds.GetRasterBand(1).WriteArray(data)
    out_ds = None