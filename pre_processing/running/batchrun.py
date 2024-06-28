from pathlib import Path 
import sys 
import os
cur = Path.cwd()
up_dir = cur.parent 
working = f'{up_dir}/working'
pre_processing = f'{up_dir}/pre_processing'
post_processing = f'{up_dir}/post_processing'
input_d = f'{up_dir}/input'
sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
# importing modules 
import sensitivity_config as cfg 
from barbel_model import FishEnvironment 
from exporting import Export
from pre_processing.phenomena import CommonMeuse, Fish 
import pcraster 
import pcraster.framework as pcrfw 

# If input extent and timedomain is not yet formatted, run following lines:: 
# commonBarbel = Fish(cfg.nr_barbel, cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.input_d)
# commonMeuse = CommonMeuse (cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.spatial_resolution, cfg.map_nc, cfg.timesteps, cfg.temporal_resolution, cfg.data_T_res, cfg.input_d)
# commonMeuse.extent() # generates a csv file describing the extent of the Meuse
# commonBarbel.extent() # generetes a csv file describing coordinatesets for each barbel
# commonMeuse.time_domain()
for fishadventuring in cfg.fish_exploring.keys():
    for fishattitude in cfg.attitude.keys():
        for spawningrange in cfg.spawning_conditions.keys():
            # Create a folder for this parameter combination
            folder_name = f"{fishattitude}_{fishadventuring}_{spawningrange}"
            folder_path = os.path.join(cfg.sens_output_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            print (f'running the config: {fishattitude}_{fishadventuring}_{spawningrange}')
            myModel = FishEnvironment(cfg.input_d, folder_path, cfg.map_nc, cfg.spatial_resolution, cfg.temporal_resolution, cfg.conversion_T, cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.nr_barbel, cfg.spawning_conditions[f'{spawningrange}'], cfg.adult_conditions, cfg.fish_exploring[f'{fishadventuring}'], cfg.attitude[f'{fishattitude}'])
            dynFrw = pcrfw.DynamicFramework(myModel, cfg.timesteps)
            dynFrw.run()
            # exporting the results to csvs, gpgks and tifs
            print (f'exporting the config:{fishattitude}_{fishadventuring}_{spawningrange}')
            export = Export(folder_path, cfg.timesteps, cfg.spatial_resolution)
            export.Barbel()
            print ('exporting barbel csvs...:')
            export.Barbel_csv()
            print ('exporting clump csvs...:')
            export.CommonMeuse_clumpcsv()
            print ('exporting spawn csvs...:')
            export.CommonMeuse_csv('spawn')
            export.Barbel_gpkg()
            export.CommonMeuse_tif('spawn')
            export.CommonMeuse_tif('connected_swim')
            print (f'done with the config: {fishattitude}_{fishadventuring}_{spawningrange}')
