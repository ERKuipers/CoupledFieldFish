import datetime
import os
import pcraster as pcr
import pcraster.framework as pcrfw
import csv
import campo

seed = 5 # to make sure random values generated are similar the second time running the program
pcr.setrandomseed(seed)
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/")


with open ('bulls_coordinates.csv', 'w', newline ='') as csvfile: # creating a file
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
        
        #add location of bulls
        self.bulls.add_property_set('char', 'bulls_coordinates.csv') # length of number of elements should be two (coordinates) for it to be a point agent or 6 for it to be a field agent

        # set initial random age of bulls
        self.bulls.char.lower = 0 # days
        self.bulls.char.upper = 50
        self.bulls.char.age = campo.uniform(self.bulls.char.lower, self.bulls.char.upper, seed)

        self.bulls.set_epsg(28992)

        self.timestep = 1 # one day 
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.month
        stepsize = 4


        # technical detail
        self.bulls.char.age.is_dynamic = True
    
        self.timestep = 1
        # create the output lue data set
        self.fishenv.create_dataset("fish_environment1.lue") #create lue environment to add time(steps) to: 
        self.fishenv.set_time(start, unit, stepsize, self.nrTimeSteps())
        # create real time settings for lue
        date = datetime.date(2000, 1, 2)
        time = datetime.time(12, 34)
        start = datetime.datetime.combine(date, time)
        unit = campo.TimeUnit.day # stepsize is day so each fish just gets older every day
        stepsize = 1
        # write the lue dataset
        self.fishenv.write()

        # print the run duration
        end = datetime.datetime.now() - init_start
        print(f'init: {end}')

    def dynamic(self):
    
        start = datetime.datetime.now()

        # update age
        self.bulls.char.age = self.bulls.char.age + 1 *self.timestep
        #self.timestep 
                       
        # print run duration info
        self.fishenv.write(self.currentTimeStep())
        end = datetime.datetime.now() - start
        print(f'ts:  {end}  write')

if __name__ == "__main__":
    timesteps = 12
    myModel = FishEnvironment()
    dynFrw = pcrfw.DynamicFramework(myModel, timesteps)
    dynFrw.run()
