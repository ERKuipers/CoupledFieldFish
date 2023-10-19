import lue.data_model as ldm
import campo
import numpy as np
import pandas 
import matplotlib.pyplot as plt
import datetime 
os.chdir("C:/Users/els-2/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/")

dataset = ldm.open_dataset('fish_environment1.lue')
for i in range(1, 13):
    dataframe = campo.dataframe.select(dataset.bulls, property_names=['age']) # can only access specific coordinates for a property, not for a property set 
    #### get the coordinates for each agent #### 
    # for a specific property set # 
    coords = dataframe ['bulls']['char']['age']['coordinates']



## now try with property set: 