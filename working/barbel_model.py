
#%%
# importing campo #
import datetime
import os
import sys
from pathlib import Path
import pcraster as pcr
import pcraster.framework as pcrfw
import campo
import numpy as np 
from matplotlib import pyplot as plt
from lookup import window_values_to_feature
from lifecycle_pref import two_conditions_boolean_prop, campo_clump
from moving_to_coordinates import coordinatelist_to_fieldloc, connected_move

#########
# model #
#########

class FishEnvironment(pcrfw.DynamicModel, ):
    def __init__(self, input_dir, output_dir, ut_array, dt_array, spatial_resolution, xmin, ymin, nrbarbels, spawning_conditions, adult_conditions):
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
        self.spawning_conditions = spawning_conditions
        self.adult_conditions = adult_conditions

    def initial(self):
        init_start = datetime.datetime.now()
        self.fishenv = campo.Campo(seed = 1)

        # create real time settings for lue: 
        date = datetime.date(2019, 6, 1)
        time = datetime.time(00,00)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.hour
        stepsize = 12
        
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
     
        # Property describing their lifestatus 
        self.barbel.adults.lifestatus = 0
        self.barbel.adults.lifestatus.is_dynamic = True # barbel age changes over time and barbel items are mobile  
        self.barbel.adults.spawning_area = 0 # describing the total available spawning area for each individual barbel
        self.barbel.adults.spawning_area.is_dynamic = True 
        self.barbel.adults.has_spawned =0 
        self.barbel.adults.has_spawned.is_dynamic = True
        self.barbel.adults.distance_to_spawn = 0
        self.barbel.adults.distance_to_spawn.is_dynamic = True
        self.barbel.adults.surrounding = 0 
        self.barbel.adults.surrounding.is_dynamic = True
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
        self.water.area.water_depth.is_dynamic = True
        self.water.area.spawning_grounds = two_conditions_boolean_prop (self, self.water.area.water_depth, self.water.area.flow_velocity, self.spawning_conditions)
        self.water.area.spawning_grounds.is_dynamic = True
        self.water.area.swimmable = two_conditions_boolean_prop (self, self.water.area.water_depth, self.water.area.flow_velocity, self.adult_conditions)
        self.water.area.swimmable.is_dynamic = True 
        self.water.area.connected_swimmable = campo_clump (self, self.water.area.swimmable)
        self.water.area.connected_swimmable.is_dynamic = True 

        self.fishenv.write() # write the lue dataset
        end = datetime.datetime.now() - init_start # print the run duration
        print(f'init: {end}, timestep: {self.currentTimeStep()}')

    def dynamic(self):
        start = datetime.datetime.now()
        # first setting environmental variables, then positioning the barbels as a response to the alternation in habitat
        self.water.area.water_depth = self.dt_array [:,self.currentTimeStep(), :,:]
        self.water.area.flow_velocity = self.ut_array [:,self.currentTimeStep(), :,:]
        self.water.area.spawning_grounds = two_conditions_boolean_prop (self, self.water.area.water_depth, self.water.area.flow_velocity, self.spawning_conditions)
        self.water.area.swimmable = two_conditions_boolean_prop(self, self.water.area.water_depth, self.water.area.flow_velocity, self.adult_conditions)
        # move them within their connected swimmable areas
        self.water.area.connected_swimmable = campo_clump (self, self.water.area.swimmable)
        movingX, movingY, spawning_area, travel_distance, has_spawned = connected_move (self, self.water.area.connected_swimmable, self.water.area.swimmable, self.water.area.spawning_grounds, self.barbel.adults, self.water.area, self.resolution, self.xmin, self.ymin, self.nrbarbels, self.currentTimeStep(), self.barbel.adults.has_spawned) 
        # move agents over field: 
        barbel_coords = self.barbel.adults.get_space_domain(self.currentTimeStep())
        barbel_coords.xcoord = movingX
        barbel_coords.ycoord = movingY
        self.barbel.adults.set_space_domain(barbel_coords, (self.currentTimeStep ())) 
        self.barbel.adults.spawning_area = spawning_area
        self.barbel.adults.has_spawned = has_spawned
        self.barbel.adults.justswam = travel_distance
        self.barbel.adults.distance_to_spawn = self.barbel.adults.distance_to_spawn + self.barbel.adults.justswam # keep on adding the swimming distance
        self.barbel.adults.surrounding = window_values_to_feature (self.barbel.adults, self.water.area, self.water.area.water_depth, 30, 'mean')
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write, timestep: {self.currentTimeStep()}')

