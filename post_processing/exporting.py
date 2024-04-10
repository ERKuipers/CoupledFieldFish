#%%
import model_config as cfg
import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
from pathlib import Path
import os 
import sys
import xarray as xr
import csv
post_processing = Path.cwd()
sys.path.append(str(post_processing))
up_dir = post_processing.parent

input_d = up_dir / 'input'
output_d = up_dir / 'output'


map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV =input_d / 'barbel_coords.csv'
fish_env = output_d / 'fish_environment.lue'
dataset = ldm.open_dataset(f"{fish_env}")
timesteps = cfg.timesteps
resolution = cfg.spatial_resolution
dyn_timevector = np.arange (0,(int(timesteps)),1) # herein the timevector says 0, but the actual timestep is 1 
coords_timevector = np.arange(1,(int(timesteps)+1),1) # no clue if 1 is then 0 or whatsoever
nr_clumps = np.zeros ((timesteps))
os.chdir(output_d) #      

#change it to make sure outputs are stored 
df = campo.dataframe.select(dataset.water, property_names=['flow_velocity']) # space type = static_diff_field but should be dynamic field 
# no space type distinction, however proper shape
spawn_df = campo.dataframe.select(dataset.water, property_names=['spawning_grounds'])
depth_df = campo.dataframe.select(dataset.water, property_names=['water_depth'])
swim_df = campo.dataframe.select(dataset.water, property_names=['swimmable'])
connected_swim_df = campo.dataframe.select (dataset.water, property_names=['connected_swimmable'])
dataframe_coords = campo.dataframe.select (dataset.barbel, property_names = ['lifestatus'])
area_df = campo.dataframe.select(dataset.barbel, property_names =['spawning_area'])
campo.to_csv(area_df, f'available_area')
distance_df = campo.dataframe.select(dataset.barbel, property_names =['distance_to_spawn'])
campo.to_csv(distance_df, f'propdist')

#for t in agent_timevector: 
for t in dyn_timevector:
     # let op : neemt alleen laatste key mee!!!!! als df 

    raster = df["water"]["area"]['flow_velocity'][0][t] # type = xarray.core.dataarray.DataArray
    spawnraster = spawn_df["water"]["area"]['spawning_grounds'][0][t] 
    depthraster = depth_df["water"]["area"]['water_depth'][0][t]
    swimraster = swim_df['water']["area"]['swimmable'][0][t]
    connected_swimraster = connected_swim_df['water']["area"]['connected_swimmable'][0][t]
    nr_clumps [t] = np.max (connected_swimraster)

    campo.to_geotiff(swimraster, (f"swim_{t+1}.tif"), 'EPSG:28992') # writing t+1 because the 0 timestep is the first (see notes 26/3)
    campo.to_geotiff(raster, (f"flow_{t+1}.tif"), 'EPSG:28992')
    campo.to_geotiff(spawnraster, (f'spawn_{t+1}.tif'), 'EPSG:28992')
    campo.to_geotiff(depthraster, (f'depth_{t+1}.tif'), 'EPSG:28992')
    campo.to_geotiff(connected_swimraster, (f"connected_swim_{t+1}.tif"), 'EPSG:28992')
print (nr_clumps)
clump_csv = output_d / "clump.csv"
with open(f'{clump_csv}', 'w', newline='') as f:
    # Create a CSV writer object
    csv_writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(nr_clumps)
#%%
for t_coords in coords_timevector:
    coords = campo.dataframe.coordinates(dataset, "barbel", "adults", t_coords) 
    tmp_df = campo.to_df(dataframe_coords, t_coords)  # is only for dataframe before starting at t =1 
    campo.mobile_points_to_gpkg(coords, tmp_df,(f"barbel_{t_coords}.gpkg"), 'EPSG:28992')

# adding environmental data 
plt.figure(1)
plt.imshow(depthraster, cmap='viridis') # uc_mag is de magnitude van de stroomsnelheid.
plt.colorbar ()
plt.show()


