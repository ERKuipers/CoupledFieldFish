# -*- coding: utf-8 -*-
#%% 
import pandas as pd
from matplotlib import pyplot as plt

import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np
import os
# rasterize function
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
    xr_raster = uds[str(var)].isel(time=timestep).ugrid.rasterize(resolution) 
    
    xr_ds = xr_raster.rio.write_crs ("epsg:28992")
    xr_df = xr_ds.to_dataframe() 
    pd_xy = xr_df.reset_index()[['x','y', str(var)]]

    reshaped = pd_xy.pivot(index = ['x'], columns = ['y'], values=str(var))
    raster_array = reshaped.to_numpy()
    return raster_array


def partial_reraster (ugrid_filelocation, resolution, timestep, var,xmin,xmax,ymin,ymax):
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

    x_coords = np.arange(xmin,xmax, resolution)     # resolution becomes the cell length of the raster.
    y_coords = np.arange(ymin,ymax,resolution)

    da_clone = xr.DataArray(data=np.ones((len(x_coords), len(y_coords))), 
                            coords={'x':x_coords,
                                    'y':y_coords},
                            dims=['x', 'y']) 



    xr_raster = uds[str(var)].isel(time=timestep).ugrid.rasterize_like(da_clone)
    xr_ds = xr_raster.rio.write_crs ("epsg:28992")   # xr Data array
    xr_df = xr_ds.to_dataframe() 
    pd_xy = xr_df.reset_index()[['x','y', str(var)]]
    # make from long raster format with columns x,y and variable the indx x, columns y and the variable the value
    reshaped = pd_xy.pivot(index = ['x'], columns = ['y'], values=str(var))  
    raster_array = reshaped.to_numpy()
    # print (raster_array.shape)
    # raster_mirroredx = np.rot90(raster_array, k=1)
    # raster_mirrored = np.flip(raster_array, axis=0)
    return raster_array

