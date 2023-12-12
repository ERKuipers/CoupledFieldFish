import pandas as pd
from matplotlib import pyplot as plt

import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np
import os
from xugrid_func import partial_reraster 
#os.environ["NUMBA_DISABLE_JIT"] = 1 
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch"
os.chdir(scratch_dir) 
map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc" #netcdf 
resolution = 5
timestep = 1
xmin,xmax = 178250, 179000
ymin,ymax = 330000, 331000

map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc" #netcdf 
resolution = 5
timesteps = np.arange (1,1930, 720)
t = 20 
xmin,xmax = 178250, 179000
ymin,ymax = 330000, 331000 
raster = np.zeros (len(timesteps))
raster1 = partial_reraster (map_nc, resolution, t, 'mesh2d_waterdepth', xmin,xmax,ymin,ymax)
raster2 = partial_reraster (map_nc, resolution, 1920, 'mesh2d_waterdepth', xmin,xmax, ymin, ymax)

plt.figure(1)
plt.imshow(raster1, cmap='viridis') # uc_mag is de magnitude van de stroomsnelheid.
plt.colorbar ()
plt.show()

plt.figure(2)
plt.imshow(raster2, cmap='viridis')

