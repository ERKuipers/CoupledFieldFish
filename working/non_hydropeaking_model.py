
#%%
# importing campo #
import datetime
import os
import sys
from pathlib import Path
cur = Path.cwd()
up_dir = cur.parent
post_processing = up_dir / 'post_processing'
working = up_dir / 'working'
sys.path.append(f'{post_processing}')
sys.path.append(f'{working}')
from pathlib import Path
import pcraster as pcr
import pcraster.framework as pcrfw
import campo
import numpy as np 
import pandas as pd
from matplotlib import pyplot as plt
from lifecycle_pref import two_conditions_boolean_prop, campo_clump
from moving_to_coordinates import move
from xugrid_func import MovingAverage_reraster

#########
# model #
#########

class FishEnvironment(pcrfw.DynamicModel):
    def __init__(self, input_dir, output, map_nc, spatial_resolution, temporal_resolution, conversion_T, xmin, ymin, xmax, ymax, nrbarbels, spawning_conditions, adult_conditions, radius, attitude, filtersize, data_DeltaTimestep):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone
        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)
        self.input_dir = input_dir 
        self.output = output 
        self.map_nc = map_nc
        self.resolution = spatial_resolution
        self.delta_t = temporal_resolution # delta timesteps
        self.xmin = xmin
        self.ymin = ymin 
        self.xmax = xmax
        self.ymax = ymax
        self.nrbarbels = nrbarbels
        self.spawning_conditions = spawning_conditions
        self.adult_conditions = adult_conditions
        self.radius = radius
        self.attitude = attitude
        self.conversion_T = conversion_T # t to multiply the timesteps with to make it fit the timestep of the model 
        self.filtersize = filtersize
        self.data_DeltaTimestep = data_DeltaTimestep
    def initial(self):
        init_start = datetime.datetime.now()
        self.fishenv = campo.Campo(seed = 1)

        # create real time settings for lue: 
        date = datetime.date(2019, 6, 1)
        time = datetime.time(00,00)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.hour
        stepsize = self.delta_t
        
        # create the output lue data set
        self.fishenv.create_dataset(f'{self.output}/fish_environment.lue')
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        self.data_t = int(self.currentTimeStep()*self.conversion_T) 
        ###################
        # Phenomenon barbel #
        ###################
        self.barbel = self.fishenv.add_phenomenon ('barbel') # could we possibly reduce the first step of this? 
        self.barbel.set_epsg(28992)
        # Property Set barbel 
        self.barbel.add_property_set ('adults', self.input_dir / 'Fish.csv' ) # the water area always has the same spatial as well as temporal extent (it always exists)
        
        self.barbel.adults.is_mobile = True
     
        # Property describing their movemode
        self.barbel.adults.movemode = 0
        self.barbel.adults.movemode.is_dynamic = True # barbel age changes over time and barbel items are mobile  
        self.barbel.adults.spawning_area = 0 # describing the total available spawning area for each individual barbel
        self.barbel.adults.spawning_area.is_dynamic = True 
        self.barbel.adults.has_spawned = 0 
        self.barbel.adults.has_spawned.is_dynamic = True
        self.barbel.adults.swimdistance = 0
        self.barbel.adults.swimdistance.is_dynamic = True
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
        self.water.area.zero = 0 
        self.water.area.one = 1
        #  Property Flow velocity # 
        u_array = pd.read_csv(f'{self.input_dir}/waterdepth_{self.currentTimeStep()}.csv' , sep=',', header=None)
        self.water.area.flow_velocity = (u_array.to_numpy()) [np.newaxis, :, :]
        self.water.area.flow_velocity.is_dynamic = True
        # Property Water Depth # 
        d_array = pd.read_csv(f'{self.input_dir}/flowvelocity_{self.currentTimeStep()}.csv' , sep=',', header=None)
        self.water.area.water_depth = (d_array.to_numpy()) [np.newaxis, :, :]
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
        self.data_t = int(self.currentTimeStep()*self.conversion_T) # update the  given data timestep with updated current timestep as by the pcraster framework 
        # first setting environmental variables, then positioning the barbels as a response to the alternation in habitat
        u_array = pd.read_csv(f'{self.input_dir}/flowvelocity_{self.currentTimeStep()}.csv' , sep=',', header=None)
        self.water.area.flow_velocity = (u_array.to_numpy()) [np.newaxis, :, :]

        # Property Water Depth # 
        d_array = pd.read_csv(f'{self.input_dir}/waterdepth_{self.currentTimeStep()}.csv' , sep=',', header=None)
        self.water.area.water_depth = (d_array.to_numpy()) [np.newaxis, :, :]
        # creating boolean and clump fields describing swimmable and spawning grounds
        self.water.area.spawning_grounds = two_conditions_boolean_prop (self, self.water.area.water_depth, self.water.area.flow_velocity, self.spawning_conditions)
        self.water.area.swimmable = two_conditions_boolean_prop(self, self.water.area.water_depth, self.water.area.flow_velocity, self.adult_conditions)
        self.water.area.connected_swimmable = campo_clump (self, self.water.area.swimmable)

        # Moving barbel and updating information about barbel movement: 
        movingX, movingY, spawning_area, travel_distance, has_spawned, movemode = move (self.water.area.connected_swimmable, self.water.area.swimmable, self.water.area.spawning_grounds, self.barbel.adults, self.water.area, self.currentTimeStep(), self.barbel.adults.has_spawned, self.radius, self.attitude) 
        # move agents over field: 
        barbel_coords = self.barbel.adults.get_space_domain(self.currentTimeStep())
        barbel_coords.xcoord = movingX
        barbel_coords.ycoord = movingY
        self.barbel.adults.set_space_domain(barbel_coords, (self.currentTimeStep ())) 
        self.barbel.adults.spawning_area = spawning_area
        self.barbel.adults.has_spawned = has_spawned
        self.barbel.adults.justswam = travel_distance
        self.barbel.adults.movemode = movemode
        self.barbel.adults.swimdistance = self.barbel.adults.swimdistance + self.barbel.adults.justswam # keep on adding the swimming distance

        # write to lue 
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write, timestep: {self.currentTimeStep()}')

