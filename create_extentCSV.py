
from xugrid_func import ugrid_rasterize
import pandas as pd
#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir) 
map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc" #netcdf 
resolution = 5
xr_array = ugrid_rasterize(map_nc, resolution,20)

# make pandas dataframe and get min and max values
pd_xy = (xr_array.to_dataframe()).reset_index()[['x','y']]
min_x = pd_xy [['x']].min().values# how do i know if this is the right way to define the raster--> cell centr so i should change this !! 
min_y = pd_xy [['y']].min().values
max_x  = pd_xy [['x']].max().values
max_y  = pd_xy [['y']].max().values
x_cells = pd_xy[['x']].nunique() # unique nr of x cells = width in x direction
y_cells = pd_xy[['y']].nunique() # unique nr of y cells = length in y direction 
# pd_xy.to_csv('water_xy_res5.csv', index = False, header = False)
# xr_array.rio.to_raster('ucmag_t20_res5.tif')

extent_df = pd.DataFrame({
    'Max X': max_x,
    'Min X': min_x,
    'Max Y': max_y,
    'Min Y': min_y,
    'Width': x_cells['x'],
    'Length': y_cells['y']
    
})
extent_df.to_csv('waterextent.csv', index = False, header = False)