#%%
from pathlib import Path
import os 
import sys
cur_dir = Path.cwd()
up_dir = cur_dir.parent
working = up_dir / 'working'
post_processing = up_dir / 'post_processing'
sys.path.append(f'{working}')
sys.path.append(str(post_processing))
import model_config as cfg
import lue.data_model as ldm
import campo
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import csv


class Export(): 
    def __init__ (self, output_d, timesteps, spatial_resolution): 
        self.output_dir = output_d
        self.timesteps = timesteps 
        self.dyn_timevector = np.arange (0,(int(timesteps)),1)
        self.coords_timevector = np.arange (1,(int(timesteps)+1),1)
        self.spatial_resolution = spatial_resolution
        self.fish_env = self.output_dir / f'fish_environment.lue'
        self.dataset  = ldm.open_dataset(f"{self.fish_env}")
    def Barbel (self): 
        self.movemode_df = campo.dataframe.select (self.dataset.barbel, property_names = [f'movemode'])
        self.has_spawned_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'has_spawned'])
        self.barbelarea_available_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'spawning_area'])
        self.distance_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'swimdistance'])
    def Barbel_csv (self): 
        campo.to_csv(self.barbelarea_available_df, f'{self.output_dir}/available_area')
        campo.to_csv(self.distance_df, f'{self.output_dir}/distance_swam')
        campo.to_csv (self.movemode_df, f'{self.output_dir}/movemode')
        campo.to_csv (self.has_spawned_df, f'{self.output_dir}/has_spawned_df')

    def CommonMeuse (self): 
        #change it to make sure outputs are stored 
        self.flow_velocity_df = campo.dataframe.select(self.dataset.water, property_names=[f'flow_velocity']) # space type = static_diff_field but should be dynamic field 
        # no space type distinction, however proper shape
        self.spawn_df = campo.dataframe.select(self.dataset.water, property_names=[f'spawning_grounds'])
        self.depth_df = campo.dataframe.select(self.dataset.water, property_names=[f'water_depth'])
        self.swim_df = campo.dataframe.select(self.dataset.water, property_names=[f'swimmable'])
        self.connected_swim_df = campo.dataframe.select (self.dataset.water, property_names=[f'connected_swimmable'])

    def CommonMeuse_csv (self): 
        
        nr_clumps = np.zeros ((self.timesteps+1))
        total_spawnarea = np.zeros ((self.timesteps+1))
        #for t in agent_timevector: 
        for t in self.dyn_timevector:
            # let op : neemt alleen laatste key mee!!!!! als df 

            raster = self.flow_velocity_df["water"]["area"]['flow_velocity'][0][t] # type = xarray.core.dataarray.DataArray
            spawnraster = self.spawn_df["water"]["area"]['spawning_grounds'][0][t] 
            depthraster = self.depth_df["water"]["area"]['water_depth'][0][t]
            swimraster = self.swim_df['water']["area"]['swimmable'][0][t]
            connected_swimraster = self.connected_swim_df['water']["area"]['connected_swimmable'][0][t]
            nr_clumps [t+1] = np.max (connected_swimraster)
            total_spawnarea [t+1] = resolution**2*np.sum(spawnraster)


        clump_csv = output_d / "clump.csv"
        with open(f'{clump_csv}', 'w', newline='') as f:
            # Create a CSV writer object
            csv_writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(nr_clumps)
        totalspawnarea_csv = output_d / "total_spawnarea.csv"
        with open(f'{totalspawnarea_csv}', 'w', newline='') as f:
            # Create a CSV writer object
            csv_writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(total_spawnarea)

    def CommonMeuse_tif (self): 
        for t in dyn_timevector:
                #change it to make sure outputs are stored 
            flow_velocity_df = campo.dataframe.select(self.dataset.water, property_names=[f'flow_velocity']) # space type = static_diff_field but should be dynamic field 
            # no space type distinction, however proper shape
            spawn_df = campo.dataframe.select(self.dataset.water, property_names=[f'spawning_grounds'])
            depth_df = campo.dataframe.select(self.dataset.water, property_names=[f'water_depth'])
            swim_df = campo.dataframe.select(self.dataset.water, property_names=[f'swimmable'])
            connected_swim_df = campo.dataframe.select (self.dataset.water, property_names=[f'connected_swimmable'])
            campo.to_geotiff(swimraster, (f"swim_{t+1}.tif"), 'EPSG:28992') # writing t+1 because the 0 timestep is the first (see notes 26/3)
            campo.to_geotiff(raster, (f"flow_{t+1}.tif"), 'EPSG:28992')
            campo.to_geotiff(spawnraster, (f'spawn_{t+1}.tif'), 'EPSG:28992')
            campo.to_geotiff(depthraster, (f'depth_{t+1}.tif'), 'EPSG:28992')
            campo.to_geotiff(connected_swimraster, (f"connected_swim_{t+1}.tif"), 'EPSG:28992')

    def Barbel_gpkg (self): 
        for t_coords in self.coords_timevector:
            coords = campo.dataframe.coordinates(self.dataset, "barbel", "adults", t_coords) 
            tmp_df = campo.to_df(self.movemode_df, t_coords)  # is only for dataframe before starting at t =1 
            campo.mobile_points_to_gpkg(coords, tmp_df,(f"barbel_{t_coords}.gpkg"), 'EPSG:28992')

        # adding environmental data 
        # plt.figure(1)
        # plt.imshow(depthraster, cmap='viridis') # uc_mag is de magnitude van de stroomsnelheid.
        # plt.colorbar()
        # plt.show()

if __name__ == "__main__":
    export = Export(cfg.output_dir, cfg.timesteps, cfg.spatial_resolution)
    export.Barbel()
    export.CommonMeuse()
    export.Barbel_csv()
    export.CommonMeuse_csv()