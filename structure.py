import datetime
import os
import pcraster as pcr
import pcraster.framework as pcrfw
from xugrid import ugrid_rasterize
import campo

seed = 5
pcr.setrandomseed(seed)

scratch_dir = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/scratch"
os.chdir(scratch_dir)
general = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish"
maas_extent = "C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/maps/water_xy.csv"
babybulls_pref = 'babybulls_pref.xlsx'

class FishEnvironment(pcrfw.DynamicModel):

    def __init__(self):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone
        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)


    def initial(self):
        init_start = datetime.datetime.now()

        self.fishenv = campo.Campo()
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4
        

        # set the duration (years) of one time step
        self.timestep = 0.333333

        # create the output lue data set
        self.fishenv.create_dataset("food_environment.lue")
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        # self.fishenv.add_phenomenon ('bulls')
        # self.fishenv.bulls.add_property_set ('bulls_loc', 'bull_agents.shp')  # --> convert to .csv for campo
        # self.fishenv.bulls.set_epsg(28992)
        self.water = self.fishenv.add_phenomenon ('water') # could we possibly reduce the first step of this? 
        self.water.add_property_set ('area', maas_extent) # the water area always has the same spatial as well as temporal extent (it always exists)
        
        self.timestep = 0
        # set crs
  
        # write the lue dataset
        self.fishenv.write()

        # print the run duration
        end = datetime.datetime.now() - init_start
        print(f'init: {end}')

    def dynamic(self):
        start = datetime.datetime.now()
        self.timestep += 1 
        self.fishenv.water.area.flow_velocity =  ('flow_velocity'+str(self.timestep)+'.tif') # overwriting flow velocity for a specific timestep to 
        
        # add from the surroundings function
        self.fishenv.bulls.add_property_set ('surroundings', 'age_related_buffer'+str(self.timestep) +'.tif' ) 
        # call surroundings function and add to bulls phenomenon: likelihood of travel 
        
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')


if __name__ == "__main__":
    timesteps = 12
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()


