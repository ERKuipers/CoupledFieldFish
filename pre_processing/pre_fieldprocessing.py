
#%%
from xugrid_func import ugrid_rasterize
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir) 
map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc" #netcdf 
resolution = 5
timestep = 1
reshaped = ugrid_rasterize(map_nc, resolution, timestep, 'mesh2d_ucmag')

plt.imshow(reshaped[3000:3400, 6000:7000], cmap='viridis')
plt.colorbar()
plt.show ()

#%% 
min_x = pd_xy [['x']].min().values# how do i know if this is the right way to define the raster--> cell centr so i should change this !! 
min_y = pd_xy [['y']].min().values
max_x  = pd_xy [['x']].max().values
max_y  = pd_xy [['y']].max().values
x_cells = pd_xy[['x']].nunique() # unique nr of x cells = width in x direction
y_cells = pd_xy[['y']].nunique() # unique nr of y cells = length in y direction 
# pd_xy.to_csv('water_xy_res5.csv', index = False, header = False)
# xr_array.rio.to_raster('ucmag_t20_res5.tif')

extent_df = pd.DataFrame({
    'Min X': min_x,
    'Max X': max_x,
    'Min Y': min_y,
    'Max Y': max_y,
    'Width': x_cells['x'],
    'Length': y_cells['y']
    })
extent_df.to_csv('waterextent.csv', index = False, header = False)