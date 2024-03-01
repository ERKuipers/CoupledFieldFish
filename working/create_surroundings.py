import geopandas as gpd 
import numpy as np
import pcraster as pcr
import campo


def get_surrounding(start_prop_agent, dest_prop_field, buffer_size):
    # re-use the previous approach to obtain the neighbours within a buffer
    values = numpy.zeros((len(start_prop.space_domain), len(dest_prop.space_domain)), dtype=numpy.int8)

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(28992)

    memdriver = ogr.GetDriverByName('MEMORY')
    ds = memdriver.CreateDataSource('tmp.gpkg')

    # Destination layer
    lyr_dest = ds.CreateLayer('uid', geom_type=ogr.wkbPoint, srs=spatial_ref)
    field = ogr.FieldDefn('uid', ogr.OFTInteger)
    lyr_dest.CreateField(field)

    # Plain storing of object order (id)
    for idx, p in enumerate(dest_prop.space_domain):
        point = ogr.Geometry(ogr.wkbPoint)

        point.AddPoint(p[0], p[1])
        feat = ogr.Feature(lyr_dest.GetLayerDefn())
        feat.SetGeometry(point)

        feat.SetField('uid', idx)

        lyr_dest.CreateFeature(feat)

    lyr_dest = None
    lyr_dest = ds.GetLayer('uid')

    for idx, p in enumerate(start_prop.space_domain):

        lyr_shop = ds.CreateLayer('destination_locations', geom_type=ogr.wkbPoint, srs=spatial_ref)
        # just a round buffer
        lyr_dist = ds.CreateLayer('source_buffer', geom_type=ogr.wkbPolygon, srs=spatial_ref)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(p[0], p[1])
        poly = point.Buffer(float(buffer_size.values()[idx]))
        feat = ogr.Feature(lyr_dist.GetLayerDefn())
        feat.SetGeometry(poly)
        lyr_dist.CreateFeature(feat)

        lyr_dest.SetSpatialFilter(poly)

        lyr_dest.Clip(lyr_dist, lyr_shop, options=['SKIP_FAILURES=NO'])

        for target in lyr_shop:

            uid = target.GetField('uid')
            values[idx, uid] = 1

    return values

def surroundings (var, xcoord, ycoord, radius): 
    ''' create surrounding of an agent based on: 
        - windowsize of 20 kilometres
        - preference of that fish 
        - occurrance of preferred environmental variables 
        xcoord = self.fish.barbel._space_domain.xcoord
        ycoord = self.fish.barbel._space_domain.yoord
        radius = the radius of the direction in which the 
        --> likelihood distribution as a window (not buffer since we have raster values and thus clipping as shp is inefficient) around an agent '''
        # make a buffer around the fishes location as a shp file
                
    lon = xcoord                # centre 
    lat = ycoord                # centre of the window
    # only make them move if the current location is not in the range of their preference
    # find the nearest indices in the xarray dataset # var = variable of interest to test to and to make likelihood raster from 
    lon_idx = abs(var['x'] - lon).argmin().item()
    lat_idx = abs(var['y'] - lat).argmin().item()
    # use these indexes to select for the different windows 
    window = var.sel(
            longitude=slice((lon_idx - windowsize/ 2), (lon_idx + windowsize / 2)),
            latitude=slice((lat_idx - window_size_lat) / (2, lat_idx + window_size_lat / 2)))
    window_df = window.to_dataframe() 
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