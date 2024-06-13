import numpy as np
import pcraster as pcr
import campo 
from campo.property import Property
from concurrent import futures
import copy
import matplotlib.pyplot as plt

def new_property_from_property(area_property):

    # make empty property

    new_prop = Property("_new_property_from_property_name", area_property._pset_uuid, area_property._pset_domain, area_property._shape)
    #new_prop.pset_domain = area_property.pset_domain
    # attach propertyset domain if available

    # obtain number, datatype and shape of value


    #new_prop.shape = area_property.shape
    # new_prop.dtype = area_property.dtype
    #nr_items = area_property._shape[0]

    # create and attach new value to property
    #dtype = area_property.values()[0].dtype
    #values = np.ones(area_property._shape[0], dtype)#, area_property.dtype)

    new_prop.values().values = copy.deepcopy(area_property.values().values)
    return new_prop

def set_current_clone(area_property, item_idx):

    west = area_property.space_domain.p1.xcoord[item_idx]
    north = area_property.space_domain.p1.ycoord[item_idx]

    rows = int(area_property.space_domain.row_discr[item_idx])
    cols = int(area_property.space_domain.col_discr[item_idx])

    cellsize = (area_property.space_domain.p2.xcoord[item_idx] - west ) / cols

    pcr.setclone(rows, cols, cellsize, west, north)

def spatial_operation_one_argument(area_property, spatial_operation, pcr_type):

    # generate a property to store the result
    result_prop = Property("_new_property_from_property_name", area_property._pset_uuid, area_property._pset_domain, area_property._shape)

    for item_idx, item in enumerate(area_property.values()):
    
        set_current_clone(area_property, item_idx)
        arg_raster = pcr.numpy2pcr(pcr_type, item, np.nan)
        pcr.plot(arg_raster)
        result_raster = spatial_operation(arg_raster)
        result_item = pcr.pcr2numpy(result_raster, np.nan)

        result_prop.values()[item_idx] = result_item # have to assign zero because item assignment apparently does not work since result_prop is a method
          # needs to be an array or a property? 
    return result_prop