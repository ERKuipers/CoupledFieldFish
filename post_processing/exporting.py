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
import csv


class Export(): 
    def __init__ (self, output_d, timesteps, spatial_resolution): 
        self.output_dir = output_d
        self.timesteps = timesteps 
        self.dyn_timevector = np.arange (0,(int(timesteps)),1)
        self.coords_timevector = np.arange (1,(int(timesteps)+1),1)
        self.spatial_resolution = spatial_resolution
        self.fish_env = f'{self.output_dir}/fish_environment.lue'
        self.dataset  = ldm.open_dataset(f"{self.fish_env}")
        
    def Barbel (self): 
        self.movemode_df = campo.dataframe.select (self.dataset.barbel, property_names = [f'movemode'])
        self.has_spawned_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'has_spawned'])
        self.barbelarea_available_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'spawning_area'])
        self.distance_df = campo.dataframe.select(self.dataset.barbel, property_names =[f'swimdistance'])

    def Barbel_gpkg (self): 
        for t_coords in self.coords_timevector:
            coords = campo.dataframe.coordinates(self.dataset, "barbel", "adults", t_coords) 
            tmp_df = campo.to_df(self.movemode_df, t_coords)  # is only for dataframe before starting at t =1 
            campo.mobile_points_to_gpkg(coords, tmp_df,(f"{self.output_dir}/barbel_{t_coords}.gpkg"), 'EPSG:28992')
            
    def Barbel_csv (self):
        os.chdir (f'{self.output_dir}')
        campo.to_csv(self.barbelarea_available_df, f'available_area')
        campo.to_csv(self.distance_df, f'distance_swam')
        campo.to_csv (self.movemode_df, f'movemode')
        campo.to_csv (self.has_spawned_df, f'has_spawned')

    def CommonMeuse_sumcsv (self, property): 
        #change it to make sure outputs are stored 
        # self.flow_velocity_df = campo.dataframe.select(self.dataset.water, property_names=[f'flow_velocity']) # space type = static_diff_field but should be dynamic field 
        # no space type distinction, however proper shape
        df = campo.dataframe.select(self.dataset.water, property_names=[f'{property}'])
        #self.depth_df = campo.dataframe.select(self.dataset.water, property_names=[f'water_depth'])
        # self.swim_df = campo.dataframe.select(self.dataset.water, property_names=[f'swimmable'])
        total_area = np.zeros ((self.timesteps+1))
        #for t in agent_timevector: 
        for t in self.dyn_timevector:
            # let op : neemt alleen laatste key mee!!!!! als df 
            raster = df["water"]["area"][f'{property}'][0][t] 
            total_area [t+1] = self.spatial_resolution**2*np.sum(raster)

        total_csv = f'{self.output_dir}/{property}.csv'
        with open(f'{total_csv}', 'w', newline='') as f:
            # Create a CSV writer object
            csv_writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(total_area)

    def CommonMeuse_clumpcsv (self): 
        connected_swim_df = campo.dataframe.select (self.dataset.water, property_names=[f'connected_swimmable'])
        nr_clumps = np.zeros ((self.timesteps+1))
        for t in self.dyn_timevector:
            connected_swimraster = connected_swim_df['water']["area"]['connected_swimmable'][0][t]
            nr_clumps [t+1] = np.max (connected_swimraster)

        clump_csv = f'{self.output_dir}/clump.csv'
        with open(f'{clump_csv}', 'w', newline='') as f:
            # Create a CSV writer object
            csv_writer = csv.writer(f, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(nr_clumps)

    def CommonMeuse_tif(self, property):
        '''property: may be 'connected_swim','flow_velocity','water_depth', 'swimmable', 'spawn'. Type =String'''
        df = campo.dataframe.select(self.dataset.water, property_names=[f'{property}'])
        for t in self.dyn_timevector:
            # let op : neemt alleen laatste key mee!!!!! als df 
            raster = df["water"]["area"][f'{property}'][0][t] 
            campo.to_geotiff(raster, (f"{self.output_dir}/{property}_{t+1}.tif"), 'EPSG:28992')



if __name__ == "__main__":
   print('exporting')
   export = Export(f'D:/thesis/sensitivity_output/wandering_homebody_broad_range', cfg.timesteps, cfg.spatial_resolution)
   print ('exporting waterdepth...:')
   export.CommonMeuse_tif('water_depth')

