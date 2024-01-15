#%%
import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
directory ="C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/"
os.chdir(directory)

dataset = ldm.open_dataset('fish_environment.lue')

xcoords = np.zeros ((11,33) )
ycoords = np.zeros ((11,33))
df = campo.dataframe.select(dataset.water, property_names=['flow_velocity']) # space type = static_diff_field but should be dynamic field 
# no space type distinction, however proper shape
spawn_df = campo.dataframe.select(dataset.water, property_names=['spawning_grounds'])
depth_df = campo.dataframe.select(dataset.water, property_names=['water_depth'])
for t in range(1, 6):
    coords = campo.dataframe.coordinates(dataset, "fish", "barbel", t)
     # let op : neemt alleen laatste key mee!!!!! als df 

    dataframe_age = campo.dataframe.select (dataset.fish, property_names = ['age'])
    # dataframex = campo.dataframe.select(dataset.fish, property_names=['coordx'])
    # dataframey = campo.dataframe.select(dataset.fish, property_names=['coordy'])
    tmp_df = campo.to_df(dataframe_age, t)
    campo.mobile_points_to_gpkg(coords, tmp_df, f"tmp_{t}.gpkg", 'EPSG:28992')


    raster = df["water"]["area"]['flow_velocity'][0][t - 1]
    spawnraster = spawn_df["water"]["area"]['spawning_grounds'][0][t - 1]
    depthraster = depth_df["water"]["area"]['water_depth'][0][t - 1]
    #filename = pathlib.Path(directory, f"fdata_{t}.tiff")
    # again shape is lost !! no extra acis 
    campo.to_geotiff(raster, f'flow_{t}.tif', 'EPSG:28992')
    campo.to_geotiff(spawnraster, f'spawn_{t}.tif', 'EPSG:28992')
    campo.to_geotiff(depthraster, f'depth_{t}.tif', 'EPSG:28992')
    

