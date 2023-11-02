import datetime
import os
import pcraster as pcr
import pcraster.framework as pcrfw

import campo

seed = 5
pcr.setrandomseed(seed)
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish")


class FishEnvironment(pcrfw.DynamicModel):

    def __init__(self):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone
        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)


    def initial(self):
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4
        self.babybulls_pref = 'babybulls_pref.xlsx',  
        
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        self.fishenv_add_phenomenon ('bulls')
        self.fishenv.bulls.add_property_set ('bulls_loc', 'bull_agents.shp')  # --> convert to .csv for campo
    
        self.fishenv_add_phenomenon ('water')
        self.fishenv_add_property_set ('area') # the water area always has the same spatial as well as temporal extent (it always exists)
    
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
        self.fishenv.water.area.flow_velocity =  'flow_velocity'+str(self.timestep)+'.tif') # overwriting flow velocity for a specific timestep to 
        
        self.fishenv.bulls.add_property_set ('surroundings', 'age_related_buffer'+str(self.timestep) +'.tif' ) 

        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')


if __name__ == "__main__":
    timesteps = 12
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()


