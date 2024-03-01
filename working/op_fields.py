import numpy as np
import pcraster as pcr
import campo 
from campo.property import Property
from concurrent import futures
import copy

def _new_property_from_property(area_property, multiplier):

    # make empty property

    new_prop = Property("_new_property_from_property_name", area_property._pset_uuid, area_property._pset_domain, area_property._shape)

    # attach propertyset domain if available
    #new_prop.pset_domain = area_property.pset_domain

    # obtain number, datatype and shape of value

    #new_prop.shape = area_property.shape
    #new_prop.dtype = area_property.dtype

    nr_items = area_property._shape[0]

    # create and attach new value to property
    dtype = area_property.values()[0].dtype
    values = np.ones(area_property._shape[0], dtype)#, area_property.dtype)

    new_prop.values().values = copy.deepcopy(area_property.values().values)
    return new_prop

def _spatial_operation_one_argument(area_property, spatial_operation, pcr_type):

    # generate a property to store the result
    result_prop = _new_property_from_property(area_property, 0.0)

    for item_idx, item in enumerate(area_property.values):

        _set_current_clone(area_property, item_idx)

        arg_raster = pcr.numpy2pcr(pcr_type, item, numpy.nan)

        result_raster = spatial_operation(arg_raster)
        result_item = pcr.pcr2numpy(result_raster, numpy.nan)

        result_prop.values[item_idx] = result_item

    return result_prop