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
    # print(uds.data_vars)
    var_dict = {}
    var_dict ['flow_velocity']= {'mesh2d_ucmag'}
    var_dict ['water_depth'] = {'mesh2d_waterdepth'}
    xr_raster = uds[str(var)].isel(time=timestep).ugrid.rasterize(resolution) # ugrid is de accessor hier. 
    xr_ds = xr_raster.rio.write_crs ("epsg:28992")
    
    # xr_ds.reset_index()
    # long_ds = xr_ds['mesh2d_ucmag'].unstack('x')
    xr_df = xr_ds.to_dataframe() #.reset_index(inplace=True) -->  leads to nonetype 
    # print (xr_df.columns)
    pd_xy = xr_df.reset_index()[['x','y', str(var)]]

    reshaped = pd_xy.pivot(index = ['x'], columns = ['y'], values=str(var))
    raster_array = reshaped.to_numpy()
    return raster_array


