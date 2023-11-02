import datetime
import os
import pcraster as pcr
import pandas as pd
import pcraster.framework as pcrfw
import csv
import campo

seed = 5 # to make sure random values generated are similar the second time running the program
pcr.setrandomseed(seed)
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/")


with open ('bulls_coordinates.csv', 'w', newline ='') as csvfile: # creating a file to store correct amount of csv 
        filewriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_NONNUMERIC)
        with open ('coords_grensmaas.csv', 'r') as f: # by reading a file with point coordinats
            reader = csv.reader (f)
            next(reader, None) #skip the header
            for row in reader: 
                filewriter.writerow (row [:2])

class FishEnvironment(pcrfw.DynamicModel):

    def __init__(self):
        pcrfw.DynamicModel.__init__(self)
        # Framework requires a clone

        # set a dummy clone
        pcr.setclone(10, 20, 10, 0, 0)

    ##########################
    # differential equations #
    ##########################

    # first term, differential equation internal effects
    #def aging (self,age): 
     #   older = age + 1 
      #  return older

    def initial(self):
    
        init_start = datetime.datetime.now()
        self.fishenv = campo.Campo()

        ##############
        # Fishes: start with bull #
        ##############

        # create bulls phenomenon
        self.bulls = self.fishenv.add_phenomenon('bulls')
        
        #add location of bulls # characteristics being the property set with a certain domain 
        # setting a property set by its initial domain 
        self.bulls.add_property_set('char', 'bulls_coordinates.csv') # length of number of elements should be two (coordinates) for it to be a point agent or 6 for it to be a field agent
                
        ##########################
        # set initial random age of bulls
        self.bulls.char.lower = 0 # days
        self.bulls.char.upper = 50 
        self.bulls.char.age = campo.uniform(self.bulls.char.lower, self.bulls.char.upper)

        # set crs 
        self.bulls.set_epsg(28992)

        self.timestep = 1 # one day 
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.day
        stepsize = 1

        # set as dynamic 
        self.bulls.char.age.is_dynamic = True
        
        # create the output lue data set

        self.fishenv.create_dataset("fish_environment.lue") #create lue environment to add time(steps) to and rest of domain knowledge + properties : 
        
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.day # stepsize is day so each fish just gets older every day
        stepsize = 1

        #feels like something like this should work: 
        #self.fishenv.set_space_domain ()
        #self.fishenv.moving = True 

        # print the run duration
        end = datetime.datetime.now() - init_start
        
        self.i = 0 # setting 0 as numeric simple timestep
        self.property_sets = {} # save different property set names as dictionary
        print(f'init: {end}')

    def dynamic(self):

        self.bullsxcoords = self.bulls.char._space_domain.xcoord
        self.bullsycoords = self.bulls.char._space_domain.ycoord
        coords_file = 'bulls_coordinates' + str(self.i) +  '.csv'
        with open (str(coords_file), 'w', newline = '') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_NONNUMERIC)
            for x,y in zip (self.bullsxcoords, self.bullsycoords): 
                filewriter.writerow ([x,y])

        start = datetime.datetime.now()
        self.i = self.i + self.timestep # setting manually a counter for a timestep
        changing_propertyset = str('char' + str(i))
        previous_prop = str('char' + str(i - 1))

        self.property_sets[changing_propertyset] = coords_file
        self.bulls.add_property_set(changing_propertyset, coords_file)

        # Create a dynamic property and update age
        self.bulls[changing_propertyset].is_dynamic = True
        self.bulls[changing_propertyset].age = self.bulls[previous_prop].age + 1 * self.timestep
       
        # write the lue dataset
        self.fishenv.write()
        self.fishenv.write(self.currentTimeStep())

        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')
        

if __name__ == "__main__":
    timesteps = 12

    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()
    # updating and saving the xcoords as an external variable that we can view, how do i make this dependent on the timestep and save it as such?? next step :) 
    fishes = myModel 
    fishes.dynamic() 
    xcoords = fishes.bullsxcoords
    ycoords = fishes.bullsycoords 
