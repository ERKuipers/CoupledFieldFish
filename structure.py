
# importing campo #
import datetime
import os
import pcraster as pcr
import pcraster.framework as pcrfw
import xarray as xr
import xugrid as xu
from xugrid_func import ugrid_rasterize
import campo


#
scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/scratch"
os.chdir(scratch_dir)
general = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish"
maas_extent = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch/water_xy_res5.csv"
#babybulls_pref = 'babybulls_pref.xlsx'
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
        
        self.timestep = 1
        # create the output lue data set
        self.fishenv.create_dataset("fish_environment.lue")
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())

        ####################
        # Phenomenon Water #
        ####################
        self.water = self.fishenv.add_phenomenon ('water') # could we possibly reduce the first step of this? 
        self.water.set_epsg(28992)
        # Property Set Area # 
        self.water.add_property_set ('area', test_extent) # the water area always has the same spatial as well as temporal extent (it always exists)
        print ('added the field as a domain') 
        self.water.area.lower = 0 # days
        self.water.area.upper = 1
        #  Property Flow velocity # 
        self.water.area.flow_velocity = campo.uniform(self.water.area.lower, self.water.area.upper) 
        self.water.area.flow_velocity.is_dynamic = True
        # Property Water Depth # 
        self.water.area.water_depth = campo.uniform(self.water.area.lower, self.water.area.upper) 
        self.water.area.water_depth.is_dynamic = True
        # why is this now static? 

        ###################
        # Phenomenon Fish #
        ###################
        self.fish = self.fishenv.add_phenomenon ('fish') # could we possibly reduce the first step of this? 
        self.fish.is_mobile = True 
        self.fish.set_epsg(28992)
        # Property Set Salmon 
        self.fish.add_property_set ('salmon', loc_CSV ) # the water area always has the same spatial as well as temporal extent (it always exists)
        self.fish.salmon.lower = 0 # days
        self.fish.salmon.upper = 50
        # Property Age
        self.fish.salmon.age = campo.uniform(self.fish.salmon.lower, self.fish.salmon.upper)
        self.fish.salmon.age.is_dynamic = True # salmon age changes over time and salmon items are mobile 
        # Properties Coordinates        
        self.fish.salmon.coordx = (self.fish.salmon.get_space_domain(self.timestep)).xcoord 
        self.fish.salmon.coordy = (self.fish.salmon.get_space_domain(self.timestep)).xcoord 
        self.fish.salmon.coordx.is_dynamic = True # mobility is dynamic haha 
        self.fish.salmon.coordy.is_dynamic = True 


        self.timestep = 0   
        self.fishenv.write() # write the lue dataset
        end = datetime.datetime.now() - init_start # print the run duration
        print(f'init: {end}')

    def dynamic(self):
        start = datetime.datetime.now()
        
        ds_u = (ugrid_rasterize (map_nc, 5, self.timestep, 'flow_velocity')) # properties can have the following shape: np.ndarray, or property.Property, or int or float. 
        self.water.area.flow_velocity = ds_u['mesh2d_ucmag'].values
        #self.water.area.water_depth = (ugrid_rasterize (map_nc, 5, self.timestep, 'water_depth')).values
        self.timestep += 1 
        print (self.timestep)
        # self.water.area.water_depth = (ugrid_rasterize (map_nc, 5, self.timestep)).values 

        # add from the surroundings function
        # self.fishenv.bulls.add_property_set ('surroundings', 'age_related_buffer'+str(self.timestep) +'.tif' ) 
        # call surroundings function and add to bulls phenomenon: likelihood of travel 
        # move agents over field: 
        salmon_coords = self.fish.salmon.get_space_domain(self.timestep)
        self.fish.salmon.coordy = salmon_coords.ycoord
        self.fish.salmon.coordx = salmon_coords.xcoord 
        # bouncing off of the border 
        salmon_coords.xcoord = campo.where (self.water.area.flow_velocity > 0, self.fish.salmon.coordx + 1, self.fish.salmon.coordx - 1) 
        salmon_coords.ycoord = campo.where (self.water.area.flow_velocity > 0, self.fish.salmon.coordy + 1, self.fish.salmon.coordy - 1)
        
        self.fish.salmon.set_space_domain(salmon_coords, self.timestep)

        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')


if __name__ == "__main__":
    timesteps = 12
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()







