from pathlib import Path

import sys
in_dir = Path.cwd()
up_dir = in_dir.parent
working = up_dir / 'working'
sys.path.append(str(working))
import model_config as cfg
from barbel_model import FishEnvironment 
from phenomena import CommonMeuse, Fish 
import pcraster as pcr
import pcraster.framework as pcrfw

commonBarbel = Fish(cfg.nr_barbel, cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.input_d)
commonMeuse = CommonMeuse (cfg.xmin, cfg.ymin, cfg.xmax, cfg.ymax, cfg.spatial_resolution, cfg.map_nc, cfg.timesteps, cfg.temporal_resolution, cfg.data_T_res, cfg.input_d)

commonMeuse.extent() # generates a csv file describing the extent of the Meuse
commonBarbel.extent() # generetes a csv file describing coordinatesets for each barbel
commonMeuse.time_domain()
u = commonMeuse.flow_velocity_array()
d = commonMeuse.waterdepth_array()

if __name__ == "__main__":
    myModel = FishEnvironment(cfg.input_d, cfg.output_f, u, d, cfg.spatial_resolution, cfg.temporal_resolution, cfg.xmin, cfg.ymin, cfg.nr_barbel, cfg.spawning_conditions, cfg.adult_conditions, cfg.dt_radius, cfg.attitude)
    dynFrw = pcrfw.DynamicFramework(myModel, cfg.timesteps)
    dynFrw.run()

