from pathlib import Path 

# directory hierarchies 
working = Path.cwd()
up_dir = working.parent
input_d = up_dir / 'input'
output_d = up_dir / 'output'
post_processing = up_dir / 'post_processing'

# data 
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV = input_d / 'barbel_coords.csv'

xmin,ymin = 179000, 329000
xmax,ymax = 180000, 331000 
spatial_resolution = 10     # metres ,  on the flexible mesh 

# temporal resolution # 
temporal_resolution = 12    # delta timestep of the model, in hours 
data_T_res = 0.5            # data delta timestep in hours 
timesteps = 5               # nr of timesteps 

# common barbel 
nr_barbel = 10