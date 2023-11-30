#%%
import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/")

dataset = ldm.open_dataset('fish_environment.lue')
xcoords = np.zeros ((11,33) )
ycoords = np.zeros ((11,33))
for t in range(1, 11):
    
    dataframe = campo.dataframe.select(dataset.fish, property_names=['coordx'])
    # campo.to_tiff(dataframe, 'flow.tif', 'EPSG:28992', i)
    coords = dataframe['fish']['salmon']['age']['coordinates']
    for i in range(len (coords['id'])):
        xcoords[t,i]= (coords.sel(id=i)[0].values.tolist()) # --> no update in the .lue framework when altering the .lue
        ycoords[t,i]= (coords.sel(id=i)[1].values.tolist())
#%% plotting and other dataformats
 
campo.to_csv(dataframe, "salmon.csv") # creates a csv for every variable so there will be a 'bulls_age', as well as a bulls_x 
age_csv = pandas.read_csv("bulls_age.csv") # so this csv is created in the previous step 
age_csv.plot(legend=False, xlabel="time steps (1 step = 1 day)", ylabel="age")
plt.savefig("bulls_age.pdf")
