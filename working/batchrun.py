from pathlib import Path 
import sys 
cur = Path.cwd()
up_dir = cur.parent 
working = up_dir / f'working'
pre_processing = up_dir / f'pre_processing'
post_processing = up_dir / f'post_processing'
input_d = up_dir / f'input'
up_output_dir = up_dir / "output"
sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
# importing modules 
import sensitivity_config as cfg 
from barbel_model import FishEnvironment 
from phenomena import CommonMeuse, Fish 
import pcraster 
import pcraster.framework as pcrfw 

commonBarbel = Fish(cfg.nr_barbel, cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.input_d)
commonMeuse = CommonMeuse (cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.spatial_resolution, cfg.map_nc, cfg.timesteps, cfg.temporal_resolution, cfg.data_T_res, cfg.input_d)
commonMeuse.extent() # generates a csv file describing the extent of the Meuse
commonBarbel.extent() # generetes a csv file describing coordinatesets for each barbel
commonMeuse.time_domain()
for fishadventuring in cfg.fish_exploring.keys():
    for fishattitude in cfg.attitude.keys():
        for spawningrange in cfg.spawning_conditions.keys():
            # Create a folder for this parameter combination
            folder_name = f"{fishattitude}_{fishadventuring}_{spawningrange}"
            folder_path = os.path.join(up_output_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            if __name__ == "__main__":
                print (f'running the config: {fishattitude}_{fishadventuring}_{spawningrange}')
                myModel = FishEnvironment(cfg.input_d, folder_path, cfg.map_nc, cfg.spatial_resolution, cfg.temporal_resolution, cfg.conversion_T, cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.nr_barbel, cfg.spawning_conditions[f'{spawningrange}'], cfg.adult_conditions, cfg.fish_exploring[f'{fishadventuring}'], cfg.attitude[f'{fishattitude}'])
                dynFrw = pcrfw.DynamicFramework(myModel, cfg.timesteps)
                dynFrw.run()
                # exporting the results to csvs, gpgks and tifs
                print (f'exporting the config:{fishattitude}_{fishadventuring}_{spawningrange}')
                export = Export(cfg.output_dir, cfg.timesteps, cfg.spatial_resolution)
                export.Barbel()
                export.CommonMeuse()
                export.Barbel_csv()
                export.CommonMeuse_csv()
                export.Barbel_gpgk()
                export.CommonMeuse_tif()
                print (f'done with the config: {fishattitude}_{fishadventuring}_{spawningrange}')
