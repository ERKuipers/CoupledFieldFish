# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 16:53:10 2023

@author: Straa005
"""
#%% 
# from osgeo import gdal
#import netCDF4
#import shapely
#import geopandas as gpd
import xarray as xr
import xugrid as xu # CIRCULAR DEPENDENCY of the package
# dependencies = inspect.getmodule(xu).__all__
#import rioxarray
#import geopandas as gpd
import numpy as np
import os
import matplotlib.pyplot as plt

#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir)
#%% open and inspect
map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc"
ds = xr.open_dataset(map_nc)
uds = xu.UgridDataset(ds)
print(uds.data_vars) # dit zijn de namen van de hydrodynamische modeluitvoer. 


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
gdf = uds['mesh2d_ucmag'].isel(time=20).ugrid.to_geodataframe()
gdf.to_file('test.gpkg')

#%% rasterize
# whole area
raster_full = uds['mesh2d_ucmag'].isel(time=20).ugrid.rasterize(40) # ugrid is de accessor hier. 

# small area
# first create a clone in xarray format use as a template for the output raster.
x_coords = np.arange(178250, 179000, 5) # 5 becomes the cell length of the raster.
y_coords = np.arange(330000, 331000, 5)

da_clone = xr.DataArray(data=np.ones((len(y_coords), len(x_coords))), 
                        coords={'x':x_coords,
                                'y':y_coords},
                        dims=['y', 'x']) 
da_clone.plot()

raster = uds['mesh2d_ucmag'].isel(time=20).ugrid.rasterize_like(da_clone)
raster.plot()

raster.rio.to_raster('test.tif')