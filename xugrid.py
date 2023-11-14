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
import xugrid as xu # CIRCULAR DEPENDENCY of the package with geopandas and xarray
import xarray as xr

# dependencies = inspect.getmodule(xu).__all__
#import rioxarray
# import geopandas as gpd # GEOPANDAS IS alread y a dependency of xugrid
import numpy as np
import os
import matplotlib.pyplot as plt

#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir) 
maas_extent = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/maps/water_xy.csv"
#%% open and inspect
map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc"

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
    uds = xu.UgridDataset(ds)
    #%% plot example data
    fig, [ax0, ax1] = plt.subplots(nrows=1, ncols=2, sharey=True,figsize=(10,6))
    uds['mesh2d_ucmag'].isel(time=20).\
        ugrid.plot(add_colorbar=True, cmap='viridis', vmax=1,
                   ax=ax0) # uc_mag is de magnitude van de stroomsnelheid.
    uds['mesh2d_node_z'].ugrid.plot(vmin=10)
    ax0.set_aspect('equal', adjustable='box')
    plt.subplots_adjust(wspace=0.55)
    plt.draw()
    plt.savefig('figure.png',dpi=380)
    
    #%% to geodataframe
    # timesteps = len(uds['mesh2d_ucmag'])
    gdf = uds['mesh2d_ucmag'].isel(time=20).ugrid.to_geodataframe()
    gdf.to_csv(maas_extent, index=False)
    gdf.to_file('test.gpkg')
    
    #%% rasterize
    # whole area
    # ugrid.rasterize(resolution as in spacing in x and y by sampling)

    xr_raster = uds['mesh2d_ucmag'].isel(time=timestep).ugrid.rasterize(resolution) # ugrid is de accessor hier. 
    
    # small area
    # first create a clone in xarray format use as a template for the output raster.
    x_coords = np.arange(178250, 179000, 5) # 5 becomes the cell length of the raster.
    y_coords = np.arange(330000, 331000, 5)
    
    da_clone = xr.DataArray(data=np.ones((len(y_coords), len(x_coords))), 
                            coords={'x':x_coords,
                                    'y':y_coords},
                            dims=['y', 'x']) 
    da_clone.plot()
    
    #raster = uds['mesh2d_ucmag'].isel(time=20).ugrid.rasterize_like(da_clone) #flow velocity in raster 
    #raster.plot()
    return xr_raster
ugrid_rasterize(map_nc, 5,20).rio.to_raster('ucmag_t20_res5.tif')