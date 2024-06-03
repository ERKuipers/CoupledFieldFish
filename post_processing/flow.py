import os
import sys
import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
cur = Path.cwd()
up_dir = cur.parent
post_processing = up_dir / 'post_processing'
sys.path.append(f"{post_processing}") 
input_d = up_dir / 'input'
sys.path.append(f"{input_d}") 
import sensitivity_config as cfg
import matplotlib.dates as mdates
import seaborn as sns 
from matplotlib.colors import ListedColormap
import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np

from scipy.signal import correlate
from scipy.stats import linregress


disk = Path("D:/thesis/")
dirNonHydro = disk / 'non_hydropeaking'
Hydro_output_d = disk / 'sensitivity_output' #"D:/thesis/sensitivity_output/"
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
discharge_csv = post_processing / '20190601_20190801_dischargeBorgharenDorp.csv'
clumps = Hydro_output_d / "focussed_traveller_broad_range/clump.csv"
fish_env = Hydro_output_d / 'fish_environment.lue'
SwimArea_f = Hydro_output_d /"focussed_homebody_broad_range/total_swimarea.csv"
BroadRangeSpawningArea_f = Hydro_output_d /"wandering_homebody_broad_range/total_spawnarea.csv"
InitialRangeSpawningArea_f = Hydro_output_d /"wandering_traveller_initial_range/total_spawnarea.csv"
noHydropeakingSpawningArea_f = dirNonHydro / "focussed_traveller_initial_range/total_spawnarea.csv"
noHydropeakingSwimArea_f = dirNonHydro / "focussed_traveller_initial_range/total_swimarea.csv"
nonHydropeaking_Clumps_f = dirNonHydro / "focussed_traveller_initial_range/clump.csv"
with open(discharge_csv, encoding='utf-8', errors='ignore') as f:  
    discharge_df = pd.read_csv(f, sep=';', header=0)

discharge_df.loc[discharge_df['ALFANUMERIEKEWAARDE'] > 1000, 'ALFANUMERIEKEWAARDE'] = np.nan
discharge_df.loc[discharge_df['ALFANUMERIEKEWAARDE'] > 300, 'ALFANUMERIEKEWAARDE'] = 300

discharge = discharge_df ['ALFANUMERIEKEWAARDE']
date_strseries = discharge_df['WAARNEMINGDATUM']
time_strseries = discharge_df['WAARNEMINGTIJD (MET/CET)']
date_parsed = pd.to_datetime(date_strseries, format="%d-%m-%Y") 
time_parsed = pd.to_datetime (time_strseries, format="%H:%M:%S").dt.time
real_time_Q = date_parsed + pd.to_timedelta(time_parsed.astype(str))
df_TimeDischarge = pd.DataFrame({'time': real_time_Q, 'discharge': discharge})
df_TimeDischarge.set_index ('time', inplace=True)
df_TimeDischarge = df_TimeDischarge [~df_TimeDischarge.index.duplicated(keep='first')]

#filtering discharge: 
df_movingAvg_discharge = pd.DataFrame(df_TimeDischarge['discharge'].resample('2H').mean().rolling(window=12, min_periods=1).mean())

# model timesteps: 
start = datetime(2019, 5, 31, 20, 0, 0)
stepsize = timedelta(hours=cfg.temporal_resolution)
nr_steps = cfg.timesteps+1
datetime_vector_clump = [start + i*stepsize for i in range(nr_steps)]
# Clumps
clumps = pd.read_csv(clumps, header = None)
df_TimeClumps = pd.DataFrame({'time': datetime_vector_clump, 'clumps': clumps.squeeze()})
df_TimeClumps.set_index ('time', inplace=True)

# combine with discharge
discharge_interp = df_TimeDischarge.reindex(df_TimeDischarge.index.union(df_TimeClumps.index)).interpolate(method='time').reindex(df_TimeClumps.index)
Discharge_Clumps = df_TimeClumps.copy()
Discharge_Clumps ['discharge']= discharge_interp['discharge']
# Drop NaN values
Discharge_Clumps.dropna(inplace=True)

discharge_normalized = (Discharge_Clumps['discharge'] - Discharge_Clumps['discharge'].mean()) / Discharge_Clumps['discharge'].std()
clumps_normalized = (Discharge_Clumps['clumps'] - Discharge_Clumps['clumps'].mean()) / Discharge_Clumps['clumps'].std()
# Calculate the normalized cross-correlation
cross_corr = correlate(discharge_normalized, clumps_normalized, mode='full')
lags = np.arange(-len(discharge_normalized) + 1, len(discharge_normalized))
# Normalize the cross-correlation values
cross_corr_normalized = cross_corr / (len(discharge_normalized) * discharge_normalized.std() * clumps_normalized.std())

# Find the lag with the maximum correlation
max_lag = lags[np.argmax(cross_corr)]
print(f"Maximum correlation at lag: {max_lag}")

# Plot the cross-correlation
plt.figure(figsize=(12, 6))
plt.plot(lags, cross_corr)
plt.axvline(x=max_lag, color='r', linestyle='--', label=f'Max Lag: {max_lag}')
plt.ylabel('Lag')
plt.xlabel('Cross-correlation')
plt.title('Cross-correlation between Discharge and Clumps')
plt.legend()
plt.grid(True)
plt.show()

# Spawnarea
InitialRangeSpawningArea = pd.read_csv(InitialRangeSpawningArea_f, header = None)
df_TimeInitialSpawn = pd.DataFrame({'time': datetime_vector_clump, 'initial_spawn': InitialRangeSpawningArea.squeeze()})
df_TimeInitialSpawn.set_index ('time', inplace=True)
BroadRangeSpawningArea = pd.read_csv(BroadRangeSpawningArea_f, header = None)
df_TimeBroadSpawn = pd.DataFrame({'time': datetime_vector_clump, 'broad_spawn': BroadRangeSpawningArea.squeeze()})
df_TimeBroadSpawn.set_index ('time', inplace=True)

# combine all with discharge
Discharge_SpawnArea = df_TimeInitialSpawn.copy()
Discharge_SpawnArea ['discharge'] = discharge_interp['discharge']
Discharge_SpawnArea ['broad_spawn'] = df_TimeBroadSpawn ['broad_spawn']

# SwimArea
SwimmingArea = pd.read_csv(SwimArea_f, header = None)
df_TimeSwim = pd.DataFrame({'time': datetime_vector_clump, 'swim': SwimmingArea.squeeze()})
df_TimeSwim.set_index ('time', inplace=True)
# combine all with discharge
Discharge_SwimArea = df_TimeSwim.copy()
Discharge_SwimArea ['discharge'] = discharge_interp['discharge']
Discharge_SwimArea ['patchsize'] = np.divide(Discharge_SwimArea ['swim'],Discharge_Clumps['clumps'])

FiltSwim = pd.read_csv(noHydropeakingSwimArea_f, header = None)
df_FiltTimeSwim = pd.DataFrame({'time': datetime_vector_clump, 'swim': FiltSwim.squeeze()})
df_FiltTimeSwim.set_index ('time', inplace=True)
FiltClumps = (pd.read_csv(nonHydropeaking_Clumps_f, header = None)).squeeze()
FiltSpawn = (pd.read_csv(noHydropeakingSpawningArea_f, header = None)).squeeze()
df_FiltTimeClump = pd.DataFrame({'time': datetime_vector_clump, 'clumps': FiltClumps}) # for some reason i cant directly import it otherwise, im too lazy to find out why
df_FiltTimeClump.set_index ('time', inplace=True)
df_FiltTimeSwim ['patchsize'] = np.divide(df_FiltTimeSwim ['swim'],df_FiltTimeClump['clumps'])
df_SpawnFilt =pd.DataFrame({'time': datetime_vector_clump, 'spawn': FiltSpawn})
df_SpawnFilt.set_index ('time', inplace=True)
df_FiltTimeSwim ['spawn'] = df_SpawnFilt ['spawn']
df_FiltTimeSwim['discharge'] = df_movingAvg_discharge['discharge']
df_FiltTimeSwim ['clumps'] = df_FiltTimeClump['clumps']
## Visualisation ##
colors = sns.color_palette("colorblind", 10) # colors = ['#8c6677','#a35641','#718f5e', '#5193bc', '#f7941d']
sns_colormap = sns.color_palette("colorblind", as_cmap=True)
colormap = ListedColormap(sns_colormap)

plt.figure(1)
plt.plot (df_TimeDischarge.index, df_TimeDischarge['discharge'], color = colors[9], label='Hydropeaking regime')
plt.plot (df_movingAvg_discharge.index, df_movingAvg_discharge['discharge'], color=colors[0], label='Filtered regime')
plt.xticks(rotation=45)
plt.xlabel('Date')
plt.ylabel ('Discharge ($m^3/s$)')
plt.show()

# habitat fragmentation: patchsize, nr of patches over discharge
fig,(ax1,ax2,ax3) = plt.subplots(3,1, figsize=(10,8))
ax1.plot (Discharge_Clumps.index, Discharge_Clumps['clumps'],color ='lightcoral', label='Hydropeaking flow regime')
ax1.plot (df_FiltTimeClump.index, df_FiltTimeClump['clumps'],color = 'darkred', linestyle='-', label='Filtered flow regime')
ax1.set_ylabel ('Number of patches')
ax1.tick_params(axis='y')
ax1.label_outer()
ax1.legend(loc='best')

#patchsize
ax2.plot(Discharge_SwimArea.index, Discharge_SwimArea['patchsize'], color='yellowgreen', label='Hydropeaking flow regime')
ax2.plot(df_FiltTimeSwim.index, df_FiltTimeSwim['patchsize'], color='darkgreen', linestyle='-', label='Filtered flow regime')
ax2.set_ylabel('Average patch size ($m^2$)')
ax2.tick_params(axis='y')
ax2.set_xlabel('Date')
ax2.tick_params(axis='x', labelrotation=45)
ax2.label_outer()
ax2.legend(loc='best')

#discharge
ax3.plot(Discharge_Clumps.index, Discharge_Clumps['discharge'], color=colors[9], label='Hydropeaking discharge')
ax3.plot(df_movingAvg_discharge.index, df_movingAvg_discharge['discharge'],color=colors[0], linestyle='-',  label ='Filtered discharge')
ax3.set_ylabel('Discharge ($m^3/s$)')
ax3.tick_params(axis='y')
ax3.set_xlabel('Date')
ax3.tick_params(axis='x', labelrotation=45)
for label in ax3.get_xticklabels():
    label.set_ha('right')
    label.set_va('top')
ax3.xaxis_date()
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formatting date
ax3.xaxis.set_major_locator(mdates.AutoDateLocator()) 
ax3.legend(loc='best')
plt.tight_layout()
plt.show()


fig,ax1 = plt.subplots()
ax1.plot(Discharge_Clumps.index, Discharge_Clumps['discharge'], color=colors[0])
ax1.set_ylabel('Discharge ($m^3/s$)', color=colors[0])
ax1.tick_params(axis='y', labelcolor=colors[0])
ax1.set_xlabel('Date')
ax1.tick_params(axis='x', labelrotation=45)
ax2 = ax1.twinx()
ax2.plot (Discharge_Clumps.index, Discharge_Clumps['clumps'],color = colors[1])
ax2.set_ylabel ('Number of clumps', color=colors[1])
ax2.tick_params(axis='y', labelcolor = colors[1])
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formatting date
ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
plt.tight_layout()
plt.show()

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 7))
# Plotting initial_spawn on ax1

# Plotting broad_spawn on ax2
ax1.plot(Discharge_SpawnArea.index[1:], Discharge_SpawnArea['broad_spawn'][1:], color=colors[2], label='Broad spawning preference')
ax1.set_ylabel('Spawn area ($m^2$)')
ax1.legend(loc='best')
ax1.tick_params(axis='y')
ax1.label_outer()


ax2.plot(Discharge_SpawnArea.index[1:], Discharge_SpawnArea['initial_spawn'][1:], color='orchid', label='Initial spawning preference')
ax2.plot(df_FiltTimeSwim.index[1:], df_FiltTimeSwim['spawn'][1:], color='indigo', label='Filtered flow regime')
ax2.set_ylabel('Spawn area ($m^2$)')
ax2.legend(loc='lower right')
ax2.tick_params(axis='y')
ax2.label_outer()
# Plotting discharge on ax3 with nicely formatted date
ax3.plot(Discharge_SpawnArea.index, Discharge_SpawnArea['discharge'], color=colors[9], label='Hydropeaking discharge')
ax3.plot(df_movingAvg_discharge.index, df_movingAvg_discharge['discharge'],color=colors[0], linestyle='-',  label ='Filtered discharge')
ax3.set_ylabel('Discharge ($m^3/s$)')
ax3.set_xlabel('Date')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formatting date
ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
ax3.tick_params(axis='x', rotation=45)
ax3.legend(loc='upper right')
for label in ax3.get_xticklabels():
    label.set_ha('right')
    label.set_va('top')
plt.tight_layout()
plt.show()

discharge_extent = np.arange(Discharge_Clumps['discharge'].min(), Discharge_Clumps['discharge'].max(),1)
filtdischarge_extent = np.arange(df_FiltTimeSwim['discharge'].min(), df_FiltTimeSwim['discharge'].max(),1)

# CLUMPS TO DISCHARGE RELATION
plt.figure() # plt.title ('Discharge and habitat fragmentation')
plt.scatter(Discharge_Clumps['discharge'], Discharge_Clumps['clumps'], s=15, color='lightcoral', label='Hydropeaking flow regime')
slope,intercept,r_value,p_value, std_err = linregress(Discharge_Clumps['discharge'],Discharge_Clumps['clumps'])

line = slope * discharge_extent + intercept
plt.plot(discharge_extent, line, color='mediumturquoise', label=f'Best fit hydropeaking: y={slope:.2f}x+{intercept:.0f}, $R^2$:{r_value:.2f}')
# now for unfiltered data: 
plt.scatter(df_FiltTimeSwim['discharge'],df_FiltTimeSwim['clumps'], s=15, color='darkred', label ='Filtered flow regime')
mask = ~np.isnan(df_FiltTimeSwim['discharge']) & ~np.isnan(df_FiltTimeSwim['clumps'])
x_clean = df_FiltTimeSwim['discharge'][mask]
y_clean = df_FiltTimeSwim['clumps'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * filtdischarge_extent + intercept
plt.plot(filtdischarge_extent, line, color='teal', label=f'Best fit filtered: y={slope:.2f}x+{intercept:.0f}, $R^2$:{r_value:.2f}')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Number of clumps')
plt.xlabel ('Discharge ($m^3/s$)')
plt.legend(loc='best', frameon=False)
plt.tight_layout()
plt.show()

#PATCHSIZE TO DISCHARGE RELATION 
plt.figure(figsize=(7.3,4)) # plt.title ('Discharge and habitat fragmentation')
plt.scatter(Discharge_SwimArea['discharge'], Discharge_SwimArea['patchsize'], s=15, color='lightcoral', label='Hydropeaking flow regime')
mask = ~np.isnan(Discharge_SwimArea['discharge']) & ~np.isnan(Discharge_SwimArea['patchsize'])
x_clean = Discharge_SwimArea['discharge'][mask]
y_clean = Discharge_SwimArea['patchsize'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * discharge_extent + intercept
plt.plot(discharge_extent, line, color='mediumturquoise', label=f'Best fit hydropeaking: \n y={slope:.2f}x+{intercept:.0f}, $R^2$:{r_value:.2f}')
# now for unfiltered data: 
plt.scatter(df_FiltTimeSwim['discharge'],df_FiltTimeSwim['patchsize'], s=15, color='darkred', label ='Filtered flow regime')
mask = ~np.isnan(df_FiltTimeSwim['discharge']) & ~np.isnan(df_FiltTimeSwim['patchsize'])
x_clean = df_FiltTimeSwim['discharge'][mask]
y_clean = df_FiltTimeSwim['patchsize'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * filtdischarge_extent + intercept
plt.plot(filtdischarge_extent, line, color='teal', label=f'Best fit filtered: \n y={slope:.2f}x+{intercept:.0f}, $R^2$:{r_value:.2f}')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Patchsize ($m^2$)')
plt.xlabel ('Discharge ($m^3/s$)')
plt.xlim([9,1000])
plt.tight_layout()
# Placing the legend
plt.legend(loc='upper right')# bbox_to_anchor=(1.5, 1))

plt.show()

# DISCHARGE TO SPAWN AREA RELATION
plt.figure() # plt.title ('Discharge and spawn area availability')

plt.scatter(Discharge_SpawnArea['discharge'], Discharge_SpawnArea['broad_spawn'], s=15, color = colors[2], label = 'Broad preferences')
mask = ~np.isnan(Discharge_SpawnArea['discharge']) & ~np.isnan(Discharge_SpawnArea['broad_spawn'])
x_clean = Discharge_SpawnArea['discharge'][mask]
y_clean = Discharge_SpawnArea['broad_spawn'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * discharge_extent + intercept
plt.plot(discharge_extent, line, color='indianred', label=f'Best fit broad: y={slope:.0f}x+{intercept:.1e}, $R^2$:{r_value:.2f}')
plt.scatter(Discharge_SpawnArea['discharge'], Discharge_SpawnArea['initial_spawn'], s=15, color = 'orchid', label = 'Initial preferences')
mask = ~np.isnan(Discharge_SpawnArea['discharge']) & ~np.isnan(Discharge_SpawnArea['initial_spawn'])
x_clean = Discharge_SpawnArea['discharge'][mask]
y_clean = Discharge_SpawnArea['initial_spawn'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * discharge_extent + intercept
plt.plot(discharge_extent, line, color='gold', label=f'Best fit initial: y={slope:.0f}x+{intercept:.1e}, $R^2$:{r_value:.2f}')
plt.scatter (df_FiltTimeSwim['discharge'],df_FiltTimeSwim['spawn'], s=15, color ='indigo', label ='Filtered flow regime')
mask = ~np.isnan(df_FiltTimeSwim['discharge']) & ~np.isnan(df_FiltTimeSwim['spawn'])
x_clean = df_FiltTimeSwim['discharge'][mask]
y_clean = df_FiltTimeSwim['spawn'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * filtdischarge_extent + intercept
plt.plot(filtdischarge_extent, line, color='darkgoldenrod', label=f'Best fit filtered: y={slope:.0f}x+{intercept:.1e}, $R^2$:{r_value:.2f}')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Spawnarea available ($m^2$)')
plt.xlabel ('Discharge ($m^3/s$)')
plt.legend(frameon=False)
plt.tight_layout()
plt.show()

#  SWIM AREA RELATION TO DISCHARGE # 
plt.figure(figsize=(7,4)) # plt.title ('Discharge and swim area availability')
plt.scatter(Discharge_SwimArea['discharge'], Discharge_SwimArea['swim'], s=15, color = 'orchid', label = 'Hydropeaking flow regime')
mask = ~np.isnan(Discharge_SwimArea['discharge']) & ~np.isnan(Discharge_SwimArea['swim'])
x_clean = Discharge_SwimArea['discharge'][mask]
y_clean = Discharge_SwimArea['swim'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * discharge_extent + intercept
plt.plot(discharge_extent, line, color='gold', label=f'Best fit initial: \n y={slope:.0f}x+{intercept:.1e}, $R^2$:{r_value:.2f}')
plt.scatter (df_FiltTimeSwim['discharge'],df_FiltTimeSwim['swim'], s=15, color ='indigo', label ='Filtered flow regime')
mask = ~np.isnan(df_FiltTimeSwim['discharge']) & ~np.isnan(df_FiltTimeSwim['swim'])
x_clean = df_FiltTimeSwim['discharge'][mask]
y_clean = df_FiltTimeSwim['swim'][mask]
slope,intercept,r_value,p_value, std_err = linregress(x_clean,y_clean)
line = slope * filtdischarge_extent + intercept
plt.xlim([9,2000])
plt.plot(filtdischarge_extent, line, color='darkgoldenrod', label=f'Best fit filtered: \n y={slope:.0f}x+{intercept:.1e}, $R^2$:{r_value:.2f}')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Swimarea available ($m^2$)')
plt.xlabel ('Discharge ($m^3/s$)')
plt.legend(loc ='upper right')
plt.tight_layout()
plt.show()