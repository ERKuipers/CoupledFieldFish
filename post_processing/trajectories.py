from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
import os
import re 
from pathlib import Path 
import sys 
import os
cur = Path("C:/Users/6402240/OneDrive - Universiteit Utrecht/Brain/Thesis/campo_tutorial/fish/CoupledFieldFish/input") #Path.cwd()
up_dir = cur.parent 
working = f'{up_dir}/working'
pre_processing = f'{up_dir}/pre_processing'
post_processing = f'{up_dir}/post_processing'
input_d = f'{up_dir}/input'
sys.path.append(f'{working}')
sys.path.append (f'{input_d}')
sys.path.append(f'{pre_processing}')
sys.path.append(f'{post_processing}')
# importing modules 
import sensitivity_config as cfg 
data_dir = Path(cfg.sens_output_dir).parent 
regimes = ['non_hydropeaking', 'sensitivity_output']
if __name__ == "__main__":
    i=0
    fig,axs = plt.subplots(2,2,figsize=(10,18))
    for spawningrange in cfg.spawning_conditions.keys():
        if spawningrange =='broad_range':
            continue
        else:
            for regime in regimes: 
                if regime == 'non_hydropeaking': 
                    name_regime = 'Filtered'
                else: 
                    name_regime = 'Hydropeaking'
                for fishadventuring in cfg.fish_exploring.keys():
                    for fishattitude in cfg.attitude.keys():
                        if fishattitude =='wandering':
                            pass
                        else: 

                            folder_name = f"{fishattitude}_{fishadventuring}_{spawningrange}"
                            folder_path = os.path.join(data_dir, regime, folder_name)
                            # Initialize an empty list to hold GeoDataFrames
                            gdfs = []

                            # Get number 
                            pattern = r'(\d+)'
                            # Loop over the files and read them
                            for filename in sorted(os.listdir(folder_path)):
                                if filename.endswith('.gpkg'):
                                    gdf = gpd.read_file(os.path.join(folder_path, filename))
                                    gdf['timestep']= int(re.split(pattern,filename)[1])  # assuming filenames are in format 0.gpkg, 1.gpkg, ...
                                    # Add an 'id' column based on the row number, as this is apparently not incorporated in the data
                                    gdf['id'] = range(1, len(gdf) + 1)
                                    gdfs.append(gdf)
                                    gdfs.append(gdf)

                            # Concatenate all GeoDataFrames
                            all_points = pd.concat(gdfs, ignore_index=True)

                            # Ensure points are sorted by ID and timestep
                            all_points = all_points.sort_values(by=['id', 'timestep'])
                            # End coords: 
                            end_coords = Point(173000, 322000)
                            zero_coords = Point(0,0)
                            for idx, row in all_points.iterrows():
                                if row.geometry == end_coords or row.geometry == zero_coords:
                                    # Get the previous timestep for the same id
                                    prev_idx = all_points[(all_points['id'] == row['id']) & (all_points['timestep'] == row['timestep'] - 1)].index
                                    if not prev_idx.empty:
                                        prev_coords = all_points.loc[prev_idx[0], 'geometry']
                                        all_points.at[idx, 'geometry'] = prev_coords
                                    else:
                                        print ('empty')
                            # Group by ID and create LineStrings
                            trajectories = all_points.groupby('id').apply(lambda x: LineString(x.geometry.tolist())).reset_index()
                            trajectories = gpd.GeoDataFrame(trajectories, geometry=0, crs=all_points.crs)

                            # now generate the points that are 
                            last_points = all_points.groupby('id').last()

                            # Convert the last points to a GeoDataFrame
                            last_points_gdf = gpd.GeoDataFrame(last_points, geometry='geometry', crs=all_points.crs)

                            # Plot trajectories
                            ax = axs[i // 2, i % 2]
                            trajectories.plot(ax=ax, linewidth=0.5, label='Trajectories')
                            last_points_gdf.plot(ax=ax, color='red', markersize=2, label='Spawn destination', zorder=2)
                            ax.legend(loc='upper left')
                            ax.set_title(f'{name_regime} {fishattitude} {fishadventuring}')
                            ax.set_xlim(cfg.xmin-1, 187000)
                            if i == 0 or i==1 or i == 3: 
                                ax.label_outer()
                            i += 1
        plt.tight_layout()
        plt.savefig(os.path.join(cfg.sens_output_dir, 'trajectory.png'))
        plt.show()
        

