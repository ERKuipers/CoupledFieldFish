
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
from lifecycle_pref import spawning
import math
#
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/working/"
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
        

        self.fishenv = campo.Campo(seed = 1)
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4
        
        self.xmin,self.xmax = 179000, 180000
        self.ymin,self.ymax = 329000, 331000
        self.resolution = 10
        self.nrrows = int(math.fabs (self.xmax - self.xmin) / self.resolution)
        self.nrcols = int(math.fabs (self.ymax - self.ymin) / self.resolution)
        with open('extent.csv', 'w') as content:
            content.write(f"{self.xmin}, {self.ymin}, {self.xmax}, {self.ymax}, {self.nrrows}, {self.nrcols}\n")

        # create the output lue data set
        self.fishenv.create_dataset("fish_environment.lue")
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        ###################
        # Phenomenon Fish #
        ###################
        self.fish = self.fishenv.add_phenomenon ('fish') # could we possibly reduce the first step of this? 
        
        self.fish.set_epsg(28992)
        # Property Set barbel 
        self.fish.add_property_set ('barbel', loc_CSV ) # the water area always has the same spatial as well as temporal extent (it always exists)
        self.fish.barbel.is_mobile = True
        self.fish.barbel.lower = 0 # days
        self.fish.barbel.upper = 20*365 #amount of half hours set to be the maximum age 
        # Property Age
        self.fish.barbel.age = campo.uniform(self.fish.barbel.lower, self.fish.barbel.upper)
        self.fish.barbel.age.is_dynamic = True # barbel age changes over time and barbel items are mobile  
        
        
        # Local properties set to 0 at first
        self.fish.barbel.waterdepth = 0 # raster_values_to_feature (self.fish.barbel, self.water.area, self.water.area.water_depth)
        self.fish.barbel.flowvelocity = 0 # raster_values_to_feature (self.fish.barbel, self.water.area, self.water.area.flow_velocity)
        self.fish.barbel.flowvelocity.is_dynamic = True 
        self.fish.barbel.waterdepth.is_dynamic = True 
        
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
        flow_array = partial_reraster(map_nc, self.resolution, self.currentTimeStep(), 'mesh2d_ucmag', self.xmin, self.xmax, self.ymin, self.ymax)
        self.water.area.flow_velocity = flow_array[np.newaxis,:, :]
        self.water.area.flow_velocity.is_dynamic = True
        # Property Water Depth # 
        depth_array = partial_reraster (map_nc, self.resolution, self.currentTimeStep(), 'mesh2d_waterdepth', self.xmin, self.xmax, self.ymin, self.ymax)
        self.water.area.water_depth = depth_array [np.newaxis,:,:]
       
        # spawning_grounds = spawning(self.water.area.water_depth, self.water.area.flow_velocity)
        #self.water.area.spawning_grounds = campo.slope (self.water.area.water_depth)
        self.water.area.water_depth.is_dynamic = True
        #_spatial_operation_two_arguments (self.water.area.water_depth, self.water.area.flow_velocity, spawning, pcraster.Boolean)
        self.water.area.deep_enough = self.water.area.water_depth >= 0.30 
        self.water.area.not_drowning = self.water.area.water_depth <= 40 # should be 0.4
        self.water.area.not_drifting = self.water.area.flow_velocity <= 50 # should be 0.5
        self.water.area.rheophilic = self.water.area.flow_velocity >=0.35 
        self.water.area.spawning_true = self.water.area.deep_enough*self.water.area.not_drowning*self.water.area.not_drifting*self.water.area.rheophilic
        self.water.area.true = 1
        self.water.area.false = 0
        self.water.area.spawning_grounds = campo.where (self.water.area.spawning_true, self.water.area.true, self.water.area.false)
        self.water.area.spawning_grounds.is_dynamic = True
        print (self.currentTimeStep())
        
        self.fishenv.write() # write the lue dataset
        end = datetime.datetime.now() - init_start # print the run duration
        print(f'init: {end}')

    def dynamic(self):
        start = datetime.datetime.now()
        self.fish.barbel.age = self.fish.barbel.age + self.currentTimeStep()  
        self.fish.barbel.waterdepth = raster_values_to_feature (self.fish.barbel, self.water.area, self.water.area.water_depth)
        self.fish.barbel.flowvelocity = raster_values_to_feature (self.fish.barbel, self.water.area, self.water.area.flow_velocity)

        # move agents over field: 
        barbel_coords = self.fish.barbel.get_space_domain(self.currentTimeStep()*48)
        barbel_coords.xcoord = self.fish.barbel.closest_spawngroundsX
        barbel_coords.ycoord = self.fish.barbel.closest_spawngroundsY
        # when moved towards dry part: swimming against the stream
        # barbel_coords.xcoord = campo.where (self.fish.barbel.waterdepth > 0, barbel_coords.xcoord + self.fish.barbel.flow_velocity, barbel_coords.xcoord - self.fish.barbel.flow_velocity)
        # barbel_coords.ycoord = barbel_coords.ycoord + 100*self.currentTimeStep ()
         
        self.fish.barbel.set_space_domain(barbel_coords, (self.currentTimeStep ()*48)) # this does not work!! space domain is set!!
        
        # self.water.area.flow_velocity = np.zeros ((1,self.nrrows, self.nrcols))
        self.water.area.deep_enough = self.water.area.water_depth >= 0.3 #.30 
        self.water.area.not_drowning = self.water.area.water_depth <= 40 #0.4
        self.water.area.not_drifting = self.water.area.flow_velocity <= 50 #0.5
        self.water.area.rheophilic = self.water.area.flow_velocity >=0.35 #.35 
        self.water.area.spawning_true =  self.water.area.deep_enough*self.water.area.not_drowning*self.water.area.not_drifting*self.water.area.rheophilic
        
        self.water.area.spawning_grounds = campo.where (self.water.area.spawning_true, self.water.area.true, self.water.area.false)


        depth_array = partial_reraster (map_nc, self.resolution, (self.currentTimeStep()*48), 'mesh2d_waterdepth', self.xmin, self.xmax, self.ymin, self.ymax)
        self.water.area.water_depth = depth_array [np.newaxis,:,:]
        flow_array = partial_reraster (map_nc, self.resolution, (self.currentTimeStep()*48), 'mesh2d_ucmag', self.xmin, self.xmax, self.ymin, self.ymax)
        self.water.area.flow_velocity = flow_array [np.newaxis,:,:]
        
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')

if __name__ == "__main__":
    timesteps = 5
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()
    flowv = myModel.water.area.flow_velocity
    array = flowv.values()[0]

    myModel.fish.barbel.get_space_domain () 

