# -*- coding: utf-8 -*-
#%% 
import xarray as xr
import xugrid as xu # CIRCULAR DEPENDENCY of the package with geopandas and xarray
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

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


