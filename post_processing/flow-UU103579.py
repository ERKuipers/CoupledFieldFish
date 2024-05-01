import pandas as pd
from matplotlib import pyplot as plt
from pathlib import Path
import xarray as xr
import xugrid as xu 
import pandas as pd
import numpy as np
import os
import sys

cur = Path.cwd()

up_dir = cur.parent
post_processing = up_dir / 'post_processing'
sys.path.append(f"{post_processing}")
input_d = up_dir / 'input'
output_d = up_dir / 'output'
map_nc = input_d / 'maas_data'/'new_fm_map.nc'
discharge_csv = post_processing / '20190601_20190801_dischargeBorgharenDorp.csv'
fish_env = output_d / 'fish_environment.lue'

discharge_df = pd.read_csv(discharge_csv)
discharge = discharge_df['ALFANUMERIEKEWAARDE']
date_strseries = discharge_df['WAARNEMINGDATUM']
time_strseries = discharge_df['WAARNEMINGTIJD (MET/CET)']
date_parsed = pd.to_datetime(date_strseries, format="%d-%m-%Y") 
time_parsed = pd.to_datetime (time_strseries, format="%H:%M:%S").dt.time
real_time = date_parsed + pd.to_timedelta(time_parsed.astype(str))

plt.figure()
plt.plot(real_time, discharge)
plt.title ('Discharge over time at Borgharen')
plt.ylabel ('Discharge ($m^3/s$)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()