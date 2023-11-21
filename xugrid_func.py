# -*- coding: utf-8 -*-
#%% 
import xarray as xr
import xugrid as xu # CIRCULAR DEPENDENCY of the package with geopandas and xarray
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

#%% rasterize function
def ugrid_rasterize (ugrid_filelocation, resolution, timestep, var):
    '''
    Parameters
    ----------
    ugrid_filelocation : location of .nc file 
    resolution : resolution to rasterize variable in 
    timestep 
    var = variable to get

    Returns
    -------
    xr_raster : xarray data array with spatial extent for that array 

    '''
    ds = xr.open_dataset(ugrid_filelocation)
    uds = (xu.UgridDataset(ds))
    print(uds.data_vars)
    var_dict = {}
    var_dict ['flow_velocity']= {'mesh2d_ucmag'}
    var_dict ['water_depth'] = {'mesh2d_waterdepth'}
    xr_raster = uds[var_dict[var]].isel(time=timestep).ugrid.rasterize(resolution) # ugrid is de accessor hier. 
    xr_rasterized = xr_raster.rio.write_crs ("epsg:28992")
    
    return xr_rasterized


