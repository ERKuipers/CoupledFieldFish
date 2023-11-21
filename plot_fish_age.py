#%%
import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/maas_data/scratch")

dataset = ldm.open_dataset('fish_environment.lue')
for i in range(1, 13):
    #dataset = ldm.open_dataset(str('fish_environment'+str(i)+'.lue'))
    dataframe = campo.dataframe.select(dataset.water, property_names=['flow_velocity'])
    campo.to_tiff(dataframe, 'flow.tif', 'EPSG:28992', i)

#%% plotting and other dataformats
dataframe = campo.dataframe.select(dataset.bulls, property_names=['age']) # you need the last (?) tuimestep 
campo.to_csv(dataframe, "bulls.csv") # creates a csv for every variable so there will be a 'bulls_age', as well as a bulls_x 
age_csv = pandas.read_csv("bulls_age.csv") # so this csv is created in the previous step 
age_csv.plot(legend=False, xlabel="time steps (1 step = 1 day)", ylabel="age")
plt.savefig("bulls_age.pdf")
