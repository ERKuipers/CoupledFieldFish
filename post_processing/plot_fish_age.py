#%%
import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
directory ="C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/"
os.chdir(directory)

dataset = ldm.open_dataset('fish_environment.lue')

xcoords = np.zeros ((11,33) )
ycoords = np.zeros ((11,33))

for t in range(1, 3):
    coords = campo.dataframe.coordinates(dataset, "fish", "salmon", t)
    flowvelocityframe = campo.dataframe.select(dataset.water, property_names=['flow_velocity', 'water_depth'])
    
    dataframe_age = campo.dataframe.select (dataset.fish, property_names = ['age'])
    # dataframex = campo.dataframe.select(dataset.fish, property_names=['coordx'])
    # dataframey = campo.dataframe.select(dataset.fish, property_names=['coordy'])
    tmp_df = campo.to_df(dataframe_age, t)
    campo.mobile_points_to_gpkg(coords, tmp_df, f"tmp_{t}.gpkg", 'EPSG:28992')

    campo.to_geotiff(flowvelocityframe, 'flow.tif', '28992', directory )

    #%% plotting and other dataformats

campo.to_csv(dataframex, "salmon.csv") # creates a csv for every variable so there will be a 'bulls_age', as well as a bulls_x 
campo.to_csv(dataframey, "salmon.csv")
xcoords_csv = pandas.read_csv("salmon_coordx.csv") # so this csv is created in the previous step 
ycoords_csv = pandas.read_csv("salmon_coordy.csv")
plt.figure (1)
for time,x in xcoords_csv.iterrows(): 
     for  time,y in ycoords_csv.iterrows():
         plt.scatter (x,y)

# xcoords_csv.plot(legend=False, xlabel="time steps (1 step = 1 day)", ylabel="xcoords")

