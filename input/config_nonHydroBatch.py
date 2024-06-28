from pathlib import Path 
import numpy as np
import math
import os
# directory hierarchies 
cur = Path.cwd()
up_dir = cur.parent
input_d = up_dir / 'input'

sens_output_dir = f'D:/thesis/non_hydropeaking/'
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
data_T_res = 0.5            # data delta timestep in hours 
conversion_T = temporal_resolution/data_T_res
data_timesteps = 2930
timesteps =  math.floor(data_timesteps/(temporal_resolution/data_T_res))        # nr of timesteps 

# common barbel 
nr_barbel = 100

# describing the bahaivour: either adventurous vs homebody and relaxed vs assertive fish
# maximum radius of sensing and moving per day (cut up in one piece)
radius = np.array([3000,20000]) # maximal swimming per timestep, with homebody fish and adventurous fish 
dt_radius = np.multiply((temporal_resolution/24), radius)
fish_exploring = {}
fish_exploring ['homebody'] = dt_radius [0]
fish_exploring ['traveller'] = dt_radius [1]
attitude = {}
attitude ['wandering']= 'wandering'
attitude ['focussed'] = 'focussed'

# ranges of preferences 
spawning_wd_min = [0.3, 0.2] 
spawning_wd_max = [0.4, 0.5] 
spawning_u_min = [0.35, 0.275]
spawning_u_max = [0.5, 0.575] 
spawning_conditions = {}
spawning_conditions ['initial_range'] = np.array([spawning_wd_min[0], spawning_wd_max[0], spawning_u_min[0], spawning_u_max[0]])
# spawning_conditions ['broad_range'] = np.array([spawning_wd_min[1], spawning_wd_max[1], spawning_u_min[1], spawning_u_max[1]])

adult_wd_min = 0.1 
adult_wd_max = 1
adult_u_min = 0.05 
adult_u_max = 0.5 
adult_conditions = np.array([adult_wd_min, adult_wd_max, adult_u_min, adult_u_max])

# hydropeaking filter: 
filtersize =24 # 24 hours