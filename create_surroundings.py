import geopandas as gpd 
import numpy as np
import pcraster as pcr
def surroundings (self, var): 
    ''' create surrounding of an agent based on: 
        - age of fish --> area 
        - preference of that fish 
        - occurrance of preferred environmental variables 
        --> likelihood distribution as a window (not buffer since we have raster values and thus clipping as shp is inefficient) around an agent '''
        # make a buffer around the fishes location as a shp file
    windowsize = self.fishenv.fish.barbel.age * 10 #couple it to age but could be something else 
    lon = self.fish.barbel._space_domain.xcoord
    lat = self.fish.barbel._space_domain.ycoord
    # only make them move if the current location is not in the range of their preference
    # find the nearest indices in the xarray dataset # var = variable of interest to test to and to make likelihood raster from 
    lon_idx = abs(var['x'] - lon).argmin().item()
    lat_idx = abs(var['y'] - lat).argmin().item()
    # use these indexes to select for the different windows 
    window = var.sel(
            longitude=slice((lon_idx - windowsize/ 2), (lon_idx + windowsize / 2)),
            latitude=slice((lat_idx - window_size_lat) / (2, lat_idx + window_size_lat / 2)))
    window_df = window.to_dataframe() 
    # make a window that relates preference of flow velocity to actual flow velocity in to a likelihood raster 
return window_df


def preference_to_likelihood(var_windowMap, pref_min, pref_max):
    '''calculates for each window, which is a pcraster map (make it a .map) the likelihood a fish will move elsewhere on the basis of the present variables and the preferences of the fish
    : write in for loop so as to call seperate windows each time''' 
    # calculate the absolute preferable variable to calculate eventually the difference from this variable
    pref_int = pref_max - pref_min # integer
    # calculate the absolute differences between each element in var_window for each window and the preference variable (integer)
    absolute_differencesMap = np.abs(var_windowMap - pref_int) 
    # find the number with the maximum absolute difference (farthest number) within the window with values of that varaible
    farthest_number = var_windowMap[max(absolute_differencesMap)] # index on the variable windowmap with the place where the difference is the biggest (least pref)
    # make the difference as a fraction of the largest difference and then substract from 1 to generate a map where an ideal situation (close to 
    #  calculate the proportion for the variable windowmap
    proportionwindowMap = 1.0 - (np.abs(var_windowMap - farthest_number) / max(absolute_differencesMap)) 
    return proportionwindowMap