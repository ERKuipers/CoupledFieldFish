#%%
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
post_processing = Path.cwd()
sys.path.append(post_processing)
up_dir = post_processing.parent

input_d = up_dir / 'input'
output_d = up_dir / 'output'


map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV =input_d / 'barbel_coords.csv'
fish_env = output_d / 'fish_environment.lue'
dataset = ldm.open_dataset(f"{fish_env}")

os.chdir(output_d) # change it to make sure outputs are stored 
df = campo.dataframe.select(dataset.water, property_names=['flow_velocity']) # space type = static_diff_field but should be dynamic field 
# no space type distinction, however proper shape
spawn_df = campo.dataframe.select(dataset.water, property_names=['spawning_grounds'])
depth_df = campo.dataframe.select(dataset.water, property_names=['water_depth'])
swim_df = campo.dataframe.select(dataset.water, property_names=['swimmable'])
connected_swim_df = campo.dataframe.select (dataset.water, property_names=['connected_swimmable'])
dataframe_age = campo.dataframe.select (dataset.barbel, property_names = ['lifestatus'])
area_df = campo.dataframe.select(dataset.barbel, property_names =['spawning_area'])
timesteps = 5 # should make this linked
resolution = 10 
total_spawnarea = np.zeros (timesteps)
timevector = np.arange (0,timesteps,1)
for t in range(1,6):
    coords = campo.dataframe.coordinates(dataset, "barbel", "adults", t)
     # let op : neemt alleen laatste key mee!!!!! als df 

    tmp_df = campo.to_df(dataframe_age, t)  # is only for dataframe before starting at t =1 
    campo.mobile_points_to_gpkg(coords, tmp_df,(f"barbel_{t}.gpkg"), 'EPSG:28992')

    raster = df["water"]["area"]['flow_velocity'][0][t - 1] # type = xarray.core.dataarray.DataArray
    spawnraster = spawn_df["water"]["area"]['spawning_grounds'][0][t - 1] 
    total_spawnarea [t-1] = resolution**2*spawnraster.sum()
    depthraster = depth_df["water"]["area"]['water_depth'][0][t - 1]
    swimraster = swim_df['water']["area"]['swimmable'][0][t-1]
    connected_swimraster = connected_swim_df['water']["area"]['connected_swimmable'][0][t-1]

    campo.to_geotiff(swimraster, (f"swim_{t-1}.tif"), 'EPSG:28992')
    campo.to_geotiff(raster, (f"flow_{t-1}.tif"), 'EPSG:28992')
    campo.to_geotiff(spawnraster, (f'spawn_{t-1}.tif'), 'EPSG:28992')
    campo.to_geotiff(depthraster, (f'depth_{t-1}.tif'), 'EPSG:28992')
    campo.to_geotiff(connected_swimraster, (f"connected_swim_{t-1}.tif"), 'EPSG:28992')


campo.to_csv(area_df, f'available_area')
available_area_frame = pandas.read_csv('available_area_spawning_area.csv')


#%%
for t in range (5):
    available_area = available_area_frame.to_numpy()[t,:]
    plt.figure()
    plt.hist(available_area, color='lightgreen', bins=15)
    plt.xlabel ('Available spawning area ($m^2$)')
    plt.ylabel ('Number of barbel')
    plt.title (f'Timestep {t}')
    plt.show()

plt.figure()
plt.scatter (timevector*12,total_spawnarea)
plt.title ('Spawning area in Common Meuse for each timestep')
plt.xlabel ('Time in hours')
plt.ylabel ('Spawning area ($m^2$)')
plt.show()