from pathlib import Path 
import sys 
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import seaborn as sns 
from matplotlib.colors import ListedColormap
cur = Path.cwd()
up_dir = cur.parent 
working = f'{up_dir}/working'
pre_processing = f'{up_dir}/pre_processing'
post_processing = f'{up_dir}/post_processing'
input_d = f'{up_dir}/input'
output_d = f'{up_dir}/output' #cfg.sens_output_dir
disk = "D:/thesis/"
sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
import config_nonHydroBatch as cfg
import math

sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
# importing modules 


sumSpawners_overTime = np.zeros ((4, cfg.timesteps))
modesAccessed = np.zeros ((4,3))
SpawnersDistances = np.zeros((4, cfg.nr_barbel))
TotalSpawnArea_overTime = np.zeros((2,cfg.timesteps))
Barbelsw_Access_overTime = np.zeros((4,cfg.timesteps))
scenarios = ['sensitivity_output','non_hydropeaking','newPref']
scenario_names = np.full(4, 'no_folder_yet', dtype='<U100')
b=0
for i, directory in enumerate(scenarios):
    fielddata_set = os.path.join(disk, directory, 'focussed_traveller_initial_range')
    #SpawningAreaFilename = os.path.join (fielddata_set, f'total_spawnarea.csv') 
    #SpawningArea_df = pd.read_csv(SpawningAreaFilename, header=None)
    #spawningarea_array = SpawningArea_df.to_numpy()
    #lastrow = spawningarea_array[-1,1:]
    #TotalSpawnArea_overTime [i,:] = lastrow
    for fishadventuring in cfg.fish_exploring.keys():
        if fishadventuring == 'homebody':
            pass
        else: 
            for fishattitude in cfg.attitude.keys():
                if fishattitude == 'wandering':
                    pass
                else:
                    # Create a folder for this parameter combination and link everything: 
                    folder_name = f"{fishattitude}_{fishadventuring}_initial_range"
                    folder_path = os.path.join(disk, directory, folder_name)
                    if directory == 'sensitivity_output':
                        data_setting = 'Hydropeaking'
                    elif directory == 'non_hydropeaking':
                        data_setting = 'Filtered'
                    else:
                        data_setting = 'Updated swim preferences'
                    scenario_names [b]= f"{data_setting} {fishattitude} {fishadventuring}"
                    
                    # create a 
                    spawnFilename = os.path.join(folder_path,f'has_spawned_has_spawned.csv')
                    MoveModeFilename = os.path.join (folder_path, f'movemode_movemode.csv')
                    DistanceSwamFilename = os.path.join (folder_path, f'distance_swam_swimdistance.csv')
                    BarbelAccessFilename= os.path.join (folder_path, f'available_area_spawning_area.csv')
                    Spawners_df = pd.read_csv (spawnFilename)
                    MoveMode_df = pd.read_csv (MoveModeFilename)
                    distance_df = pd.read_csv (DistanceSwamFilename)
                    
                    BarbelAccess_toSpawningArea_df = pd.read_csv (BarbelAccessFilename)
                    SpawnersDistances [b,:]= np.multiply(Spawners_df.to_numpy()[-1,:],distance_df.to_numpy()[-1,:]) 
                    modesAccessed [b,0] = np.sum (MoveMode_df.to_numpy()==2)
                    modesAccessed [b,1] = np.sum (MoveMode_df.to_numpy()==3)
                    modesAccessed [b,2] = np.divide(modesAccessed [b,0],modesAccessed[b,1])*100 
                    # modesAccessed [b,3] = np.sum (MoveMode_df.to_numpy()==1)
                    sumSpawners_overTime [b,:]= np.sum (Spawners_df.to_numpy(), axis=1)
                
                    b+=1
# categorical so pd dataframe: 
Column_MoveMode = ['Nearest', 'Directed/Random', 'Relative nearest'] 
modesAccessed_df = pd.DataFrame(modesAccessed, index=scenario_names, columns=Column_MoveMode)
SpawnersDistances_df = pd.DataFrame (SpawnersDistances, index=scenario_names)
melt_SpawnersDistances_df = SpawnersDistances_df.melt(ignore_index=False).reset_index()
melt_SpawnersDistances_df.columns = ['Configuration', 'Agent', 'Distance']

# generating the corresponding datetimevector
start = datetime(2019, 6, 1, 0, 0, 0)
stepsize = timedelta(hours=cfg.temporal_resolution)
nr_steps = cfg.timesteps
datetime_vector = [start + i*stepsize for i in range(nr_steps)]

################################################################
colors = sns.color_palette("colorblind", 10) # colors = ['#8c6677','#a35641','#718f5e', '#5193bc', '#f7941d']
del colors[1]
sns_colormap = sns.color_palette("colorblind", as_cmap=True)
colormap = ListedColormap(sns_colormap)

# Plotting 

# Plotting each line for different wandering and focussed
plt.figure(figsize=(12, 6))  # Create a 2x2 grid of subplots
# Define the indices for the lines you want to plot in each subplot


plt.plot(datetime_vector, sumSpawners_overTime[0, :], 
                label=f'{scenario_names[0]}', linestyle=['-', '--'][0], 
                color=colors[3])  
#plt.plot(datetime_vector, sumSpawners_overTime[1, :], 
                #label=f'{scenario_names[1]}', linestyle=['-', '--'][1], 
                #color=colors[2])  
plt.plot(datetime_vector, sumSpawners_overTime[2, :], 
                label=f'{scenario_names[2]}', linestyle=['-', '--'][1], 
                color=colors[0])  

#plt.xaxis.major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#plt.xaxis.major_locator(mdates.AutoDateLocator())
plt.tick_params(axis='both', labelsize=12)  # Adjust tick labels size
plt.xlabel('Date', fontsize=14)


plt.ylabel('Population\'s spawning success (%)', fontsize=13) # only set y axis label for the most right plots
plt.ylim([0,105])
plt.legend(fontsize='large', loc='lower right')
# Adjust layout to accommodate subplots
plt.tight_layout()
plt.gcf().autofmt_xdate() # Rotate dates for better readability
plt.show()



# movement modes 
fig, ax1 = plt.subplots(figsize=(10, 7)) # Movement modes accessed by the barbels in different configurations
ax1 = modesAccessed_df[['Nearest', 'Directed/Random']].plot(kind='bar', ax=ax1, figsize=(10, 7), cmap=colormap, position=0, width = 0.4)
# Movement modes accessed by the barbels in different configurations 
ax1.tick_params(axis='x', labelsize=12, labelrotation=45)
for tick in ax1.get_xticklabels():
    tick.set_horizontalalignment('right')
ax1.set_xlabel('Configurations')
ax1.set_ylabel('Times movement mode used', fontsize=13)

ax2 = ax1.twinx()

modesAccessed_df[['Relative nearest']].plot(kind='bar', ax=ax2, figsize=(10, 7), color='orange', position=-2, width = 0.2)
ax2.set_ylabel('Relative use of neareast movement mode (%)', fontsize=13)
ax2.legend(loc='upper right')
# Adding legend
ax1.legend(title='Movement Modes', loc='upper left', bbox_to_anchor=(0.48, 1))
plt.tight_layout()
plt.show()


