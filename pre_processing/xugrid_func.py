# -*- coding: utf-8 -*-
#%% 
import pandas as pd
from matplotlib import pyplot as plt
import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np
import os
import math
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
    reshaped = pd_xy.pivot(index = ['y'], columns = ['x'], values=str(var))  
    raster_array_rev = reshaped.to_numpy()
    raster_array = np.flip (raster_array_rev, axis = 0)
    return raster_array

def MovingAverage_reraster (ugrid_filelocation, resolution, timestep, var,xmin,xmax,ymin,ymax, filtersize, modelTemporalResolution, Data_DeltaTimestep):
    '''
    Parameters
    ----------
    ugrid_filelocation : location of .nc file 
    resolution : resolution to rasterize variable in 
    timestep: 
    filtersize: in timeunit given, so e.g. 24 hours is a running average over 24 hours
    var = variable to get

    Returns
    -------
    xr_raster : xarray data array with spatial extent for that array 

    '''
    # e.g. the half hour deltaTs for a 24 hour filtersize at timestep (data) = 62, with 2 hour model interval: should generate 12 steps 
    # (62-24/0.5/2)=38, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78, 82,(62+24/0.5/2)=86
    arrays_idxs_ToAverageOver = np.arange ((timestep-((filtersize/Data_DeltaTimestep)/2)),(timestep+((filtersize/Data_DeltaTimestep)/2)+1), (modelTemporalResolution/Data_DeltaTimestep))
    
    
    nr_cols = math.floor((xmax - xmin)/ resolution)
    nr_rows = math.floor((ymax - ymin)/resolution)
    running_sum = np.zeros ((nr_rows, nr_cols))
    count = 0
    for t in arrays_idxs_ToAverageOver: 
        if t<1:
            timestep_nr=1
        elif t>2929: # im really sorry for this hardcode i will fix it later
            timestep_nr=2929
        else:
            timestep_nr= int(t)
        running_sum += partial_reraster (ugrid_filelocation, resolution, timestep_nr, var, xmin, xmax, ymin, ymax)
        count += 1
    MovingAverage_raster = running_sum / count  
    return MovingAverage_raster