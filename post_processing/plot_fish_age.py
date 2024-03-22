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
sys.path.append('C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/post_processing')
from to_tiff import to_geotiff as tf
working = Path.cwd()

up_dir = working.parent

input_d = up_dir / 'input'
output_d = up_dir / 'output'


map_nc = input_d / 'maas_data'/'new_fm_map.nc'
loc_CSV =input_d / 'barbel_coords.csv'
fish_env = output_d / 'fish_environment.lue'
dataset = ldm.open_dataset(f"{fish_env}")

os.chdir(output_d) # change it to make sure outputs are stored 

xcoords = np.zeros ((11,33)) # zo wat lelijk 
ycoords = np.zeros ((11,33))
df = campo.dataframe.select(dataset.water, property_names=['flow_velocity']) # space type = static_diff_field but should be dynamic field 
# no space type distinction, however proper shape
spawn_df = campo.dataframe.select(dataset.water, property_names=['spawning_grounds'])
depth_df = campo.dataframe.select(dataset.water, property_names=['water_depth'])
swim_df = campo.dataframe.select(dataset.water, property_names=['swimmable'])
dataframe_age = campo.dataframe.select (dataset.barbel, property_names = ['lifestatus'])
for t in range(1, 6):
    coords = campo.dataframe.coordinates(dataset, "barbel", "adults", t)
     # let op : neemt alleen laatste key mee!!!!! als df 


    tmp_df = campo.to_df(dataframe_age, t)  # is only for dataframe before timestep 0 
    campo.mobile_points_to_gpkg(coords, tmp_df,(f"barbel_{t}.gpkg"), 'EPSG:28992')


    raster = df["water"]["area"]['flow_velocity'][0][t - 1]
    spawnraster = spawn_df["water"]["area"]['spawning_grounds'][0][t - 1]
    depthraster = depth_df["water"]["area"]['water_depth'][0][t - 1]
    swimraster = swim_df['water']["area"]['swimmable'][0][t-1]
    #filename = pathlib.Path(directory, f"fdata_{t}.tiff")
    
    campo.to_geotiff(swimraster, (f"swim_{t}.tif"), 'EPSG:28992')
    campo.to_geotiff(raster, (f"flow_{t}.tif"), 'EPSG:28992')
    campo.to_geotiff(spawnraster, f'spawn_{t}.tif', 'EPSG:28992')
    campo.to_geotiff(depthraster, f'depth_{t}.tif', 'EPSG:28992')
    

