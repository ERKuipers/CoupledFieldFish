from pathlib import Path 
import numpy as np
# directory hierarchies 
working = Path.cwd()
up_dir = working.parent
input_d = up_dir / 'input'
output_d = up_dir / 'output'
post_processing = up_dir / 'post_processing'

# data 
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV = input_d / 'barbel_coords.csv'

xmin,ymin =  173000, 322000, # 179000, 329000  #
xmax,ymax =  193400, 353000 #180000, 331000 #
spatial_resolution = 10     # metres , rerasterizing the flexible mesh

# temporal resolution # 
temporal_resolution = 6    # delta timestep of the model, in hours 
data_T_res = 0.5            # data delta timestep in hours 
timesteps = 240               # nr of timesteps 

# common barbel 
nr_barbel = 100

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