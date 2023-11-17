# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 16:53:10 2023

@author: Straa005 

modified by Els Kuipers 7/11/23
- altered listing of imports to prevent circular dependency of packages 
- made function out of it 
- first opening dataset with xarray to make it a data array instead of doing that with xu 
"""
#%% 
# from osgeo import gdal
#import netCDF4
#import shapely

#import geopandas as gpd
import xarray as xr
import xugrid as xu # CIRCULAR DEPENDENCY of the package with geopandas and xarray


# dependencies = inspect.getmodule(xu).__all__
#import rioxarray
# import geopandas as gpd # GEOPANDAS IS alread y a dependency of xugrid
import numpy as np
import os
import matplotlib.pyplot as plt

#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir) 

#%% rasterize function
def ugrid_rasterize (ugrid_filelocation, resolution,timestep):
    '''


    Parameters
    ----------
    ugrid_filelocation : location of .nc file 
    resolution : resolution to rasterize variable in 
    timestep 

    Returns
    -------
    xr_raster : xarray data array with spatial extent for that array 

    '''
    ds = xr.open_dataset(ugrid_filelocation)
    uds = (xu.UgridDataset(ds))
    # uds = uds.ugrid.set_crs("EPSG:28992") # removes, strangely enough, the whol accessing
   
    # rasterize
    # whole area
    # ugrid.rasterize(resolution as in spacing in x and y by sampling)
    xr_raster = uds['mesh2d_ucmag'].isel(time=timestep).ugrid.rasterize(resolution) # ugrid is de accessor hier. 
    xr_rasterized = xr_raster.rio.write_crs ("epsg:28992")
    
    return xr_rasterized
#%% rasterize, usually this is not a very slow cell 

map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc" #netcdf 
resolution = 5
xr_array = ugrid_rasterize(map_nc, resolution,20)

#%% create csv, this is a slow cell 
pd_xy = (xr_array.to_dataframe()).reset_index()[['x','y']]
pd_xy [['x1']] = pd_xy [['x']] - (resolution/2) # how do i know if this is the right way to define the raster--> cell centr so i should change this !! 
pd_xy [['y1']] = pd_xy [['y']] - (resolution/2)
pd_xy [['x']] = pd_xy [['x']] + (resolution/2)
pd_xy [['y']] = pd_xy [['y']] + (resolution/2)
pd_xy [["i"]] = 101 
pd_xy [["j"]] = 101
pd_xy.to_csv('water_xy_res5.csv', index = False, header = False)
# xr_array.rio.to_raster('ucmag_t20_res5.tif')

#%% make a smoll csv

smoll = pd_xy.iloc[:5]
smoll.to_csv('test_waterextent.csv', index = False, header = False)