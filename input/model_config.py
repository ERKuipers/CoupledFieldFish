
from pathlib import Path 
import numpy as np
import math
import os
# directory hierarchies 
cur = Path.cwd()
up_dir = cur.parent
input_d = up_dir / 'input'

output_dir = f'D:/thesis/non_hydropeaking/'
working = up_dir / 'working'
post_processing = up_dir / 'post_processing'
file_name = 'fish_environment.lue'
# data 
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV = input_d / 'barbel_coords.csv'

xmin,ymin =  173000, 322000, # 179000, 329000  #
xmax,ymax =  193400, 353000 #180000, 331000 #
spatial_resolution = 10     # metres , rerasterizing the flexible mesh

# temporal resolution # 
temporal_resolution = 2    # delta timestep of the model, in hours 
data_T_res = 0.5            # delta timestep in hours of the input data (to translate from model to data timestep)
conversion_T = temporal_resolution/data_T_res
data_timesteps = 2930       # total number of timesteps in data available
timesteps = math.floor(data_timesteps/(temporal_resolution/data_T_res))        # nr of timesteps if we want to run complete data

# common barbel 
nr_barbel = 100

# maximum radius of sensing and moving per day (cut up in one piece)
radius = 10000 # maximal swimming per timestep
dt_radius = temporal_resolution/24*radius 
attitude = 'focussed'

# hydropeaking filter: 
filtersize =24 # 24 hours

# ranges of preferences 
spawning_wd_min = 0.3 
spawning_wd_max = 0.4 
spawning_u_min = 0.35 
spawning_u_max = 0.5
spawning_conditions = np.array([spawning_wd_min, spawning_wd_max, spawning_u_min, spawning_u_max])

adult_wd_min = 0.1 
adult_wd_max = 1 
adult_u_min = 0.05 
adult_u_max = 0.5 
adult_conditions = np.array([adult_wd_min, adult_wd_max, adult_u_min, adult_u_max])

