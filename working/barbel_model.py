
#%%
# importing campo #
import datetime
import os
import sys
from pathlib import Path
sys.path.append ("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/pre_processing/")
sys.path.append ("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish")
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
from lifecycle_pref import spawning, spawning_true, swimmable
from coordinatelist_fieldloc import coordinatelist_to_fieldloc
from op_fields import _spatial_operation_one_argument, _new_property_from_property, _set_current_clone
import math
import random
import unittest


#########
# model #
#########

class FishEnvironment(pcrfw.DynamicModel, ):

    def __init__(self, input_dir, output_dir, ut_array, dt_array, spatial_resolution, xmin, ymin, nrbarbels):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone
        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)
        self.input_dir = input_dir 
        self.output_dir = output_dir 
        self.ut_array = ut_array 
        self.dt_array = dt_array
        self.resolution = spatial_resolution
        self.xmin = xmin
        self.ymin = ymin 
        self.nrbarbels = nrbarbels

    def initial(self):
        init_start = datetime.datetime.now()
        
        self.fishenv = campo.Campo(seed = 1)

        # create real time settings for lue: 
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4
        

        # create the output lue data set
        self.fishenv.create_dataset(self.output_dir / "fish_environment.lue")
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        
        ###################
        # Phenomenon barbel #
        ###################
        self.barbel = self.fishenv.add_phenomenon ('barbel') # could we possibly reduce the first step of this? 
        self.barbel.set_epsg(28992)
        # Property Set barbel 
        self.barbel.add_property_set ('adults', self.input_dir / 'Fish.csv' ) # the water area always has the same spatial as well as temporal extent (it always exists)
        
        self.barbel.adults.is_mobile = True
     
        # Property Age
        self.barbel.adults.lifestatus = 0
        self.barbel.adults.lifestatus.is_dynamic = True # barbel age changes over time and barbel items are mobile  
        
        
        # Local properties set to 0 at first
        self.barbel.adults.waterdepth = 0 # raster_values_to_feature (self.barbel.barbel, self.water.area, self.water.area.water_depth)
        self.barbel.adults.flowvelocity = 0 # raster_values_to_feature (self.barbel.barbel, self.water.area, self.water.area.flow_velocity)
        self.barbel.adults.flowvelocity.is_dynamic = True 
        self.barbel.adults.waterdepth.is_dynamic = True 

        #change location based on spawning grounds: 
        self.barbel.adults.closest_spawngroundsX = 0  
        self.barbel.adults.closest_spawngroundsY = 0
        self.barbel.adults.closest_spawngroundsX.is_dynamic = True
        self.barbel.adults.closest_spawngroundsY.is_dynamic = True

        ####################
        # Phenomenon Water #
        ####################
        self.water = self.fishenv.add_phenomenon ('water') # could we possibly reduce the first step of this? 
        self.water.set_epsg(28992)
        # Property Set Area # 
        self.water.add_property_set ('area', self.input_dir / 'CommonMeuse.csv') # the water area always has the same spatial as well as temporal extent (it always exists)
        print ('added the field as a domain')  
        self.water.area.lower = 0 # days
        self.water.area.upper = 1
        #  Property Flow velocity # 
        self.water.area.flow_velocity = self.ut_array[:,self.currentTimeStep(), :, :]
        self.water.area.flow_velocity.is_dynamic = True
        # Property Water Depth # 
    
        self.water.area.water_depth = self.dt_array[:,self.currentTimeStep(), :, :]
        # spawning_grounds = spawning(self.water.area.water_depth, self.water.area.flow_velocity)
        #self.water.area.spawning_grounds = campo.slope (self.water.area.water_depth)
        self.water.area.water_depth.is_dynamic = True
        #_spatial_operation_two_arguments (self.water.area.water_depth, self.water.area.flow_velocity, spawning, pcraster.Boolean)
        self.water.area.spawning_grounds = spawning_true (self, self.water.area.water_depth, self.water.area.flow_velocity)
        self.water.area.spawning_grounds.is_dynamic = True
        self.water.area.swimmable = swimmable (self,'swimmable', self.water.area.water_depth, self.water.area.flow_velocity)
        self.water.area.swimmable.is_dynamic = True 
        
        self.fishenv.write() # write the lue dataset
        end = datetime.datetime.now() - init_start # print the run duration
        print(f'init: {end}')

    def dynamic(self):
        start = datetime.datetime.now()

        # self.barbel.adults.waterdepth = raster_values_to_feature (self.barbel.adults, self.water.area, self.water.area.water_depth)
        # self.barbel.adults.flowvelocity = raster_values_to_feature (self.barbel.adults, self.water.area, self.water.area.flow_velocity)
        self.water.area.spawning_grounds = spawning_true (self, self.water.area.water_depth, self.water.area.flow_velocity)
        self.water.area.swimmable = swimmable (self, 'swimmable', self.water.area.water_depth, self.water.area.flow_velocity)
        
        spawngroundsX, spawngroundsY = coordinatelist_to_fieldloc (self, self.water.area.spawning_true, self.barbel.adults, self.resolution, self.xmin, self.ymin, self.nrbarbels) 

        # move agents over field: 
        barbel_coords = self.barbel.adults.get_space_domain(self.currentTimeStep())
        barbel_coords.xcoord = spawngroundsX
        barbel_coords.ycoord = spawngroundsY

        self.barbel.adults.set_space_domain(barbel_coords, (self.currentTimeStep ())) 

        self.water.area.spawning_grounds = spawning_true (self, self.water.area.water_depth, self.water.area.flow_velocity)
        
        self.water.area.water_depth = self.dt_array [:,self.currentTimeStep(), :,:]
        self.water.area.flow_velocity = self.ut_array [:,self.currentTimeStep(), :,:]
        
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')

