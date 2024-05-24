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
import math
cur = Path.cwd()

up_dir = cur.parent 
working = f'{up_dir}/working'
pre_processing = f'{up_dir}/pre_processing'
post_processing = f'{up_dir}/post_processing'
input_d = f'{up_dir}/input'
output_d = f'{up_dir}/output' #cfg.sens_output_dir
sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
# importing modules 
import sensitivity_config as cfg 
b = 0
sumSpawners_overTime = np.zeros ((8, cfg.timesteps))
modesAccessed = np.zeros ((8,3))
SpawnersDistances = np.zeros((8, cfg.nr_barbel))
TotalSpawnArea_overTime = np.zeros((8,cfg.timesteps))
Barbelsw_Access_overTime = np.zeros((8,cfg.timesteps))
folder_names = np.full(8, 'no_folder_yet', dtype='<U100')
for fishadventuring in cfg.fish_exploring.keys():
    for fishattitude in cfg.attitude.keys():
        for spawningrange in cfg.spawning_conditions.keys():
            # Create a folder for this parameter combination
            folder_name = f"{fishattitude}_{fishadventuring}_{spawningrange}"
            folder_names [b]= folder_name
            folder_path = os.path.join(output_d, folder_name)
            spawnFilename = os.path.join(folder_path,f'has_spawned_has_spawned.csv')
            MoveModeFilename = os.path.join (folder_path, f'movemode_movemode.csv')
            DistanceSwamFilename = os.path.join (folder_path, f'distance_swam_swimdistance.csv')
            BarbelAccessFilename= os.path.join (folder_path, f'available_area_spawning_area.csv')
            # for some area properties, total spawnarea is missing but its okay because the spawning area will be the same for the same initial range (its regardless of behaviour)
            if folder_name == 'wandering_homebody_initial_range' or folder_name == 'focussed_homebody_initial_range':
                AreaFolderpath = os.path.join(output_d, f'wandering_traveller_initial_range')
            else:
                AreaFolderpath = os.path.join(output_d, folder_name)
            
            SpawningAreaFilename = os.path.join (AreaFolderpath, f'total_spawnarea.csv') 
            Spawners_df = pd.read_csv (spawnFilename)
            MoveMode_df = pd.read_csv (MoveModeFilename)
            distance_df = pd.read_csv (DistanceSwamFilename)
            SpawningArea_df = pd.read_csv(SpawningAreaFilename, header=None)
            BarbelAccess_toSpawningArea_df = pd.read_csv (BarbelAccessFilename)
            
            spawningarea_array = SpawningArea_df.to_numpy()
            lastrow = spawningarea_array[-1,1:]
            TotalSpawnArea_overTime [b,:] = lastrow
            # just the last row to get all the barbel that eventually spawn 
            
            SpawnersDistances [b,:]= np.multiply(Spawners_df.to_numpy()[-1,:],distance_df.to_numpy()[-1,:]) 
            modesAccessed [b,0] = np.sum (MoveMode_df.to_numpy()==2)
            modesAccessed [b,1] = np.sum (MoveMode_df.to_numpy()==3)
            modesAccessed [b,2] = np.sum (MoveMode_df.to_numpy()==4)
            # modesAccessed [b,3] = np.sum (MoveMode_df.to_numpy()==1)
            sumSpawners_overTime [b,:]= np.sum (Spawners_df.to_numpy(), axis=1)
            Barbelsw_Access_overTime [b,:] = np.sum (BarbelAccess_toSpawningArea_df.to_numpy() > 0, axis=1)
            
            b +=1

# categorical so pd dataframe: 
Column_MoveMode = ['Nearest', 'Directed/Random', 'Destination'] 
Row_Configuration = folder_names          
modesAccessed_df = pd.DataFrame(modesAccessed, index=Row_Configuration, columns=Column_MoveMode)
SpawnersDistances_df = pd.DataFrame (SpawnersDistances, index=Row_Configuration)
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
plt.figure(1)
plt.plot (datetime_vector, sumSpawners_overTime [0,:], label =f'{folder_names[0]}', linestyle ='--', color=colors[0])
plt.plot (datetime_vector, sumSpawners_overTime [2,:], label =f'{folder_names[2]}', linestyle ='--', color=colors[1])
plt.plot (datetime_vector, sumSpawners_overTime [4,:], label =f'{folder_names[4]}', linestyle ='-', color=colors[0])
plt.plot (datetime_vector, sumSpawners_overTime [6,:], label =f'{folder_names[6]}', linestyle ='-', color=colors[1])
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()
plt.xticks(fontsize=8)
plt.xlabel('Date', fontsize=10)
plt.ylabel('Spawning succes of population (%)', fontsize=10)
# plt.title('Spawning success over time considering different types of barbel behaviour')
plt.legend(loc='best', fontsize='small', frameon=True, fancybox=True, shadow=False)
plt.tight_layout()
plt.show()

# Plotting each line for different broad and initial spawning preferences 
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # Create a 2x2 grid of subplots

# Define the indices for the lines you want to plot in each subplot
lines_per_subplot = [[0, 1], [2, 3], [4,5], [6, 7]]
legend_entries = []
for ax, line_indices in zip(axs.flatten(), lines_per_subplot):
    for index in line_indices:
        ax.plot(datetime_vector, sumSpawners_overTime[index, :], 
                label=f'{folder_names[index]}', linestyle=['--', '-'][index % 2], 
                color=colors[math.floor(index/2)])  # Cycle through colors if needed
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.tick_params(axis='both', labelsize=12)  # Adjust tick labels size
    ax.set_xlabel('Date', fontsize=14)

    if line_indices ==[0,1] or line_indices ==[4,5]:
        ax.set_ylabel('Spawning success of population (%)', fontsize=14) # only set y axis label for the most right plots
    else: 
        ax.set_yticklabels([]) # remove tick labels for the most right plots  
    ax.set_ylim([0,100])
    ax.legend()


# Adjust layout to accommodate subplots

fig.tight_layout()
plt.gcf().autofmt_xdate() # Rotate dates for better readability
plt.show()

# Plotting each line for different wandering and focussed
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # Create a 2x2 grid of subplots

# Define the indices for the lines you want to plot in each subplot
lines_per_subplot = [[0, 2], [1, 3], [4,6], [5, 7]]
legend_entries = []
for ax, line_indices in zip(axs.flatten(), lines_per_subplot):
    for index in line_indices:
        ax.plot(datetime_vector, sumSpawners_overTime[index, :], 
                label=f'{folder_names[index]}', linestyle=['-', '--'][index % 2], 
                color=colors[math.floor(index/2)])  # Cycle through colors if needed
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.tick_params(axis='both', labelsize=12)  # Adjust tick labels size
    ax.set_xlabel('Date', fontsize=14)

    if line_indices ==[0,2] or line_indices ==[4,6]:
        ax.set_ylabel('Spawning success of population (%)', fontsize=14) # only set y axis label for the most right plots
    else: 
        ax.set_yticklabels([]) # remove tick labels for the most right plots  
    ax.set_ylim([0,100])
    ax.legend()
fig.tight_layout()
plt.gcf().autofmt_xdate() # Rotate dates for better readability
plt.show()
# Plotting each line for different wandering and focussed
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # Create a 2x2 grid of subplots

# Define the indices for the lines you want to plot in each subplot
lines_per_subplot = [[0, 4], [1, 5], [2,6], [3, 7]]
legend_entries = []
for ax, line_indices in zip(axs.flatten(), lines_per_subplot):
    for index in line_indices:
        ax.plot(datetime_vector, sumSpawners_overTime[index, :], 
                label=f'{folder_names[index]}', linestyle=['-', '--'][index % 2], 
                color=colors[math.floor(index/2)])  # Cycle through colors if needed

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.tick_params(axis='both', labelsize=12)  # Adjust tick labels size
    ax.set_xlabel('Date', fontsize=14)

    if line_indices ==[0,4] or line_indices ==[2,6]:
        ax.set_ylabel('Spawning success of population (%)', fontsize=14) # only set y axis label for the most right plots
    else: 
        ax.set_yticklabels([]) # remove tick labels for the most right plots  
    ax.set_ylim([0,100])
    ax.legend()

# Adjust layout to accommodate subplots

fig.tight_layout()
plt.gcf().autofmt_xdate() # Rotate dates for better readability
plt.show()

plt.figure(3) # Movement modes accessed by the barbels in different configurations
ax = modesAccessed_df.plot(kind='bar', stacked=True, figsize=(10, 7), cmap=colormap)
# Movement modes accessed by the barbels in different configurations 
ax.set_xlabel('Configurations')
ax.set_ylabel('Number of Times Accessed of movement modes')
# Adding legend
plt.legend(title='Movement Modes', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

