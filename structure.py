
# importing campo #
import datetime
import os
import pcraster as pcr
import pcraster.framework as pcrfw
import xarray as xr
import xugrid as xu
from xugrid_func import ugrid_rasterize
from xugrid_func import partial_reraster
import campo
import numpy as np 
from matplotlib import pyplot as plt
from lookup import raster_values_to_feature 
import math
#
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/working"
os.chdir(scratch_dir)
general = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish"
maas_extent = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch/water_xy_res5.csv"

map_nc = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/new_fm_map.nc"
test_extent = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch/waterextent.csv"
loc_CSV ="C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/bulls_coords.csv"
#########
# model #
#########
class FishEnvironment(pcrfw.DynamicModel):

    def __init__(self):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone
        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)

    def initial(self):
        init_start = datetime.datetime.now()
        self.timestep = 0 

        self.fishenv = campo.Campo()
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4
        
        xmin,xmax = 179000, 180000
        ymin,ymax = 329000, 331000
        resolution = 10
        nrrows = int(math.fabs (xmax - xmin) / resolution)
        nrcols = int(math.fabs (ymax - ymin) / resolution)
        with open('extent.csv', 'w') as content:
            content.write(f"{xmin}, {ymin}, {xmax}, {ymax}, {nrrows}, {nrcols}\n")

        # create the output lue data set
        self.fishenv.create_dataset("fish_environment.lue")
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())

        ####################
        # Phenomenon Water #
        ####################
        self.water = self.fishenv.add_phenomenon ('water') # could we possibly reduce the first step of this? 
        self.water.set_epsg(28992)
        # Property Set Area # 
        self.water.add_property_set ('area', 'extent.csv') # the water area always has the same spatial as well as temporal extent (it always exists)
        print ('added the field as a domain') 
        self.water.area.lower = 0 # days
        self.water.area.upper = 1
        #  Property Flow velocity # 
        self.water.area.flow_velocity = np.zeros ((nrrows, nrcols)) 
        # self.water.area.flow_velocity.is_dynamic = True
        # Property Water Depth # 
        self.water.area.water_depth = partial_reraster (map_nc, resolution, self.timestep, 'mesh2d_waterdepth', xmin, xmax, ymin, ymax) 
    
        # self.water.area.water_depth.is_dynamic = True
        # why is this now static? 
        # self.water.area.deep_enough = self.water.area.water_depth > 0.2 

        ###################
        # Phenomenon Fish #
        ###################
        self.fish = self.fishenv.add_phenomenon ('fish') # could we possibly reduce the first step of this? 
         
        self.fish.set_epsg(28992)
        # Property Set Salmon 
        self.fish.add_property_set ('salmon', loc_CSV ) # the water area always has the same spatial as well as temporal extent (it always exists)
        self.fish.salmon.is_mobile = True
        self.fish.salmon.lower = 0 # days
        self.fish.salmon.upper = 50
        # Property Age
        self.fish.salmon.age = campo.uniform(self.fish.salmon.lower, self.fish.salmon.upper)
        self.fish.salmon.age.is_dynamic = True # salmon age changes over time and salmon items are mobile 
        # # Properties Coordinates        

        # Add local water depth to fish 
        # campo.field_values_to_agent () --> create such a function ? 
        # self.fish.salmon.waterdepth = raster_values_to_feature (self.fish.salmon, self.water.area, self.water.area.water_depth)
        # campo.feature_to_raster(self.water.area, self.fish.salmon.)
        self.timestep = 0   
        self.fishenv.write() # write the lue dataset
        end = datetime.datetime.now() - init_start # print the run duration
        print(f'init: {end}')

    def dynamic(self):
        start = datetime.datetime.now()
        self.timestep += 1 
        #should have shape of 
        # self.water.area.flow_velocity = np.zeros ((3442,7373))
        # self.water.area.flow_velocity = ugrid_rasterize (map_nc, 5, self.timestep, 'mesh2d_ucmag')# properties can have the following shape: np.ndarray, or property.Property, or int or float. 
         #['mesh2d_ucmag'].values
        # self.water.area.water_depth = ugrid_rasterize (map_nc, 5, self.timestep, 'mesh2d_waterdepth')
        

        # move agents over field: 
        salmon_coords = self.fish.salmon.get_space_domain(self.timestep)

        # salmon_coords.xcoord = salmon_coords.xcoord + 100
        # salmon_coords.ycoord = salmon_coords.ycoord + 100
        # bouncing off of the border 
        
        salmon_coords.xcoord = salmon_coords.xcoord + 100*self.timestep
        salmon_coords.ycoord = salmon_coords.ycoord + 100*self.timestep
         
 
        self.fish.salmon.set_space_domain(salmon_coords, self.timestep) # this does not work!! space domain is set!!
        
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')


if __name__ == "__main__":
    timesteps = 3
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()
    waterdepth = myModel.water.area.flow_velocity
    array = waterdepth.values()[0]

    myModel.fish.salmon.get_space_domain () 

