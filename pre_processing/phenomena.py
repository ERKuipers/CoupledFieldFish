from pathlib import Path
import sys 
import os 
working = Path.cwd()
up_dir = working.parent 
pre_processing_dir = up_dir / 'pre_processing/'
sys.path.append(pre_processing_dir)
from pre_processing.xugrid_func import partial_reraster, MovingAverage_reraster 
import numpy as np 
import random
import math 
import csv 
class CommonMeuse(): 
    def __init__ (self, xmin, ymin, xmax, ymax, resolution, map_nc, timesteps, deltaT_mod, deltaT_data, input_dir, filtersize, modelTemporalResolution, Data_DeltaTimestep):
        '''
        Class describing the domain over which to model in relation to spatial data given for the Common Meuse. 

        deltaT_mod = timestep over which the model will be run (e.g. to run the model over 1 day, 1440 minutes)
        deltaT_data = timestep for the data (e.g. Common Meuse rastered data covers 30 minutes).
        Unit is whatever, as long as deltaT_mod and deltaT_data have the same unit
        timesteps = nr of steps to iterate the model 
        '''
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax 
        self.ymax = ymax 
        self.resolution = resolution 
        self.map_nc = map_nc
        self.timesteps = timesteps 
        self.deltaT_mod = deltaT_mod
        self.deltaT_data = deltaT_data
        self.input_dir = input_dir
        self.t_data = None  # timestep vector for data to be defined in time_domain function 
        self.filtersize = filtersize 
        self.modelTemporalResolution = modelTemporalResolution
        self.Data_DeltaTimestep = Data_DeltaTimestep
    def time_domain (self):
        '''
        Constructing a timedomain for the model in relation to the input data 
        Returns a vector with a timestep as wanted by the modeller, suitable to call the available data 
        '''                                   
        self.t_data = np.arange (0, int(self.timesteps*(self.deltaT_mod/self.deltaT_data))+1, int((self.deltaT_mod / self.deltaT_data)))  

    def extent (self):
        '''
        Generates a CSV file in which we specify the domain as required by campo
        - a field per line 
        - column 1: xmin 
        - column 2: ymin 
        - column 3: xmax
        - column 4: ymax 
        - column 5: number of rows or pixels/gridcells on the x axis 
        - column 6: number of columns or pixels / gridcells on the y axis 
        row, column herein equals x, y 
        from campo docs: 

                        x1[idx] = item[0]
                y1[idx] = item[1]
                x2[idx] = item[2]
                y2[idx] = item[3]
                xdiscr[idx] = item[4]
                ydiscr[idx] = item[5]
            self.p1.xcoord = x1
            self.p1.ycoord = y1

            self.p2.xcoord = x2
            self.p2.ycoord = y2

            self.row_discr = xdiscr , but no should be nr of y!!!!!!!! 
            self.col_discr = ydiscr
        '''
        self.nrcols = int(math.fabs (self.xmax - self.xmin) / self.resolution)
        self.nrrows = int(math.fabs (self.ymax - self.ymin) / self.resolution)
        with open(self.input_dir / 'CommonMeuse.csv', 'w') as content:
            content.write(f"{self.xmin}, {self.ymin}, {self.xmax}, {self.ymax},  {self.nrrows}, {self.nrcols}\n") 
            

    def flow_velocity_array (self): 
        '''
        Creating a 4 dimensional array describing the flow velocity with 
        - first dimension: nr of fields available, 
        - second dimension: time, 
        - third: x axis and 
        - fourth: y axis
        Row = y, Column = x, as defined in extent
        Herein data can be called on the basis of the model's timestep (second dimension), does not require configuration to the data timestep 
        the array is +1 larger than the nr of timesteps to account for the initial timestep = 0 , 
        over which the nr of timesteps is started to count in the dynamic section with t = 1 
        NB: change function 'MovingAverage_reraster' to 'partial_reraster' if you do NOT wish to make a moving average' 
        '''
        u_array = np.zeros (( self.nrrows, self.nrcols )) 
        for t_mod, t in enumerate(self.t_data):
            u_array= MovingAverage_reraster(self.map_nc, self.resolution, t, 'mesh2d_ucmag', self.xmin, self.xmax, self.ymin, self.ymax, self.filtersize, self.modelTemporalResolution, self.Data_DeltaTimestep)
            np.savetxt(f'{self.input_dir}/flowvelocity_{t_mod}.csv', u_array, delimiter=',', fmt='%s')
            print (f'timestep: {t_mod}  flow data accessed')

    
    def waterdepth_array (self): 
        '''See docstring about flow velocity array '''
        d_array = np.zeros ((self.nrrows, self.nrcols))
        for t_mod, t in enumerate(self.t_data) : 
            d_array  = MovingAverage_reraster (self.map_nc, self.resolution, t, 'mesh2d_waterdepth', self.xmin, self.xmax, self.ymin, self.ymax, self.filtersize, self.modelTemporalResolution, self.Data_DeltaTimestep)
            np.savetxt(f'{self.input_dir}/waterdepth_{t_mod}.csv', d_array, delimiter=',', fmt='%s')


class Fish(): 
    def __init__ (self, nr_fish, xmin, ymin, xmax, ymax, input_dir): 
        self.nr_fish = nr_fish 
        self.xmin = xmin 
        self.ymin = ymin
        self.xmax = xmax 
        self.ymax = ymax 
        self.input_dir = input_dir

    def extent (self): 
        ''' Generates a csv with randomly placed coordinates within the bounding box in line with the number of fish as specified by the configuration'''
        self.x = [random.uniform(self.xmin, self.xmax) for _ in range(self.nr_fish)]
        self.y = [random.uniform(self.ymin, self.ymax) for _ in range(self.nr_fish)]
        with open(self.input_dir / 'Fish.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for x, y in zip(self.x, self.y):
                writer.writerow([f"{x}", f"{y}"])

