import model_config as cfg
from barbel_model import FishEnvironment 
from generation_extent_nr import CommonMeuse, Fish 
connect(cfg.loc_CSV, cfg.xmax, cfg.ymax, cfg.ymin, cfg.xmin, cfg.map_nc)

depth_array = CommonMeuse.
if __name__ == "__main__":
    timesteps = 5
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()