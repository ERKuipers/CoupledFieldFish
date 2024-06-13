import pathlib as Path
import rasterio
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
import os
import sensitivity_config as cfg
import cmcrameri.cm as cmc

# Define the directory containing your raster files
raster_dir_initial = f'{cfg.sens_output_dir}/wandering_traveller_initial_range'
raster_dir = f'{cfg.sens_output_dir}/wandering_traveller_broad_range'
# Initialize arrays to hold the summed suitability and transition counts
sum_suitability = None
transition_count = None

# Loop through the rasters and process each one
raster_files = [os.path.join(raster_dir, f) for f in os.listdir(raster_dir) if f.endswith('.tif')]
previous_data = None

for idx, raster_file in enumerate(raster_files):
    with rasterio.open(raster_file) as src:
        data = src.read(1)  # Read the first band
        
        # Initialize arrays if they are None
        if sum_suitability is None:
            sum_suitability = np.zeros(data.shape, dtype=np.int32)
            transition_count = np.zeros(data.shape, dtype=np.int32)

        # Update the sum suitability array
        sum_suitability += data
        
        # Update the transition count array
        if previous_data is not None:
            transition_count += (data != previous_data).astype(np.int32)
        
        previous_data = data
#%%
# Since the last comparison doesn't count as a transition, subtract 1 if transition_count > 0
transition_count = np.where(transition_count > 0, transition_count - 1, 0)
sum_suitability_m = sum_suitability[sum_suitability!=0]
transition_count_m = transition_count[transition_count!=0]
average_sum_suitability = np.mean (sum_suitability_m)
average_transitioncount = np.mean (transition_count_m)
median_SumSuitability = np.median (sum_suitability_m)
median_TransitionCount = np.median (transition_count_m)
max_sum_suitability = np.max (sum_suitability_m)
max_transition_count = np.max (transition_count_m)
print
#%%
# Visualize the Results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 15))

# Plot summed suitability
suitability_plot = show(sum_suitability, ax= ax1, cmap=(cmc.batlow).reversed())
suitability_img = suitability_plot.get_images()[0]
ax1.set_title('Summed Suitability')
fig.colorbar(suitability_img, ax=ax1, orientation='vertical')

# Plot transition frequency
transition_plot = show(transition_count, ax=ax2, cmap=(cmc.batlow).reversed())
transition_img = transition_plot.get_images()[0]
ax2.set_title('Transition Frequency')
fig.colorbar(transition_img, ax=ax2, orientation='vertical')

plt.tight_layout()
plt.show()