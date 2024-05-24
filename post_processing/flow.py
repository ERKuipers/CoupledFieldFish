import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import sensitivity_config as cfg
import matplotlib.dates as mdates
import seaborn as sns 
from matplotlib.colors import ListedColormap
import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np
import os
import sys
from scipy.signal import correlate
from scipy.stats import linregress

cur = Path.cwd()
up_dir = cur.parent
post_processing = up_dir / 'post_processing'
sys.path.append(f"{post_processing}") 
input_d = up_dir / 'input'
output_d = up_dir / 'output' #"D:/thesis/sensitivity_output/"
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
discharge_csv = post_processing / '20190601_20190801_dischargeBorgharenDorp.csv'
clumps = output_d / "focussed_traveller_broad_range/clump.csv"
fish_env = output_d / 'fish_environment.lue'
BroadRangeSpawningArea_f = output_d /"wandering_homebody_broad_range/total_spawnarea.csv"
InitialRangeSpawningArea_f = output_d /"wandering_traveller_initial_range/total_spawnarea.csv"

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
plt.xlabel('Lag')
plt.ylabel('Cross-correlation')
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


## Visualisation ##
colors = sns.color_palette("colorblind", 4) # colors = ['#8c6677','#a35641','#718f5e', '#5193bc', '#f7941d']
sns_colormap = sns.color_palette("colorblind", as_cmap=True)
colormap = ListedColormap(sns_colormap)


plt.figure(1)
plt.plot(real_time_Q[:-1], discharge[:-1])
plt.title ('Discharge over time at Borgharen')
plt.ylabel ('Discharge ($m^3/s$)')
plt.xticks(rotation=45)
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

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
# Plotting initial_spawn on ax1
ax1.plot(Discharge_SpawnArea.index, Discharge_SpawnArea['initial_spawn'], color=colors[2], label='Initial spawning preference')
ax1.set_ylabel('Spawn area ($m^2$)')
ax1.legend(loc='lower right')
ax1.tick_params(axis='y')
ax1.label_outer()
# Plotting broad_spawn on ax2
ax2.plot(Discharge_SpawnArea.index, Discharge_SpawnArea['broad_spawn'], color=colors[3], label='Broad spawning preference')
ax2.set_ylabel('Spawn area ($m^2$)')
ax2.legend(loc='lower right')
ax2.tick_params(axis='y')
ax2.label_outer()
# Plotting discharge on ax3 with nicely formatted date
ax3.plot(Discharge_SpawnArea.index, Discharge_SpawnArea['discharge'], color=colors[0])
ax3.set_ylabel('Discharge ($m^3/s$)')
ax3.set_xlabel('Date')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Formatting date
ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
ax3.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.show()

plt.figure() # plt.title ('Discharge and habitat fragmentation')
plt.scatter(Discharge_Clumps['discharge'], Discharge_Clumps['clumps'], s=15, color = colors[1])
slope,intercept,r_value,p_value, std_err = linregress(Discharge_Clumps['discharge'],Discharge_Clumps['clumps'])
line = slope * Discharge_Clumps['discharge'] + intercept
plt.plot(Discharge_Clumps['discharge'], line, color=colors[3], label=f'Best fit: y={slope:.2f}x+{intercept:.1f}, $R^2$:{r_value:.0f}')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Number of clumps')
plt.xlabel ('Discharge ($m^3/s$)')
plt.legend()
plt.tight_layout()
plt.show()

plt.figure() # plt.title ('Discharge and spawn area availability')
plt.scatter(Discharge_SpawnArea['discharge'], Discharge_SpawnArea['initial_spawn'], s=15, color = colors[2], label = 'Initial preferences')
plt.scatter(Discharge_SpawnArea['discharge'], Discharge_SpawnArea['broad_spawn'], s=15, color = colors[3], label = 'Broad preferences')
plt.xscale ('log')
plt.yscale ('log')
plt.ylabel ('Spawnarea available ($m^2$)')
plt.xlabel ('Discharge ($m^3/s$)')
plt.legend()
plt.tight_layout()
plt.show()
