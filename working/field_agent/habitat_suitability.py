import campo
import pcraster as pcr 

from campo.property import Property
import numpy as np 
import matplotlib.pyplot as plt
import math
import campo
import pcraster as pcr 
# see campo documentation for these functions:
import numpy as np 



def campo_clump (boolean_fieldprop, field_pset):
    connected_boolean_prop = Property("_new_property_from_property_name", boolean_fieldprop._pset_uuid, boolean_fieldprop._pset_domain, boolean_fieldprop._shape)
    for fidx, area in enumerate (field_pset.space_domain): 
        nrCols = int(area[5])
        nrRows = int(area[4])
        west = area [0]
        north = area [3]
        cellSize = math.fabs (area[2] - west)/nrCols
    boolean_ar = (boolean_fieldprop.values()[0]).astype(int)
    plt.imshow(boolean_ar)
    plt.colorbar()
    plt.show()
    pcr.setclone (nrRows, nrCols, cellSize, west, north)
    arg_raster = pcr.numpy2pcr(pcr.Boolean, boolean_ar, -1000)
    pcr.plot(arg_raster)
    result_raster = pcr.clump(arg_raster)
    result_ar = pcr.pcr2numpy(result_raster, -1000)
    # overruling value 0 for areas that are not connected to the big 'non-swimmable land' but are still non-swimmable ! 
    # value 0 for any clump which is non-swimmable  
    #boolean_fieldprop.values()[0], shows correct but im not sure if its boolean, seems like it

    connected_boolean_ar = np.where (boolean_fieldprop.values()[0] == 0, 0, result_ar)  
    connected_boolean_prop.values()[0] = connected_boolean_ar
    return connected_boolean_prop


def two_conditions_boolean_prop (self, water_depth, flow_velocity, conditions ):
    ''' returns a boolean fieldproperty on the basis of  input conditions two (equally sized) field properties 
    and conditions determined by the modeller 
    Parameters: 
        self: model object 
        water_depth: boolean fieldproperty
        flow_v: boolean fieldproperty 
        conditions: a list with length 4, contains the conditions on the basis of which the boolean map will be created, with idx
            0: water_depth_min 
            1: water_depth_max 
            2: flow_velocity_min
            3: flow_velocity_max
    Returns: a boolean fieldprop for which both conditions in relation to flow velocity and water depth are true
        '''
    water_d = water_depth.values()[0]
    flow_v = flow_velocity.values()[0]
    water_depth_min = conditions[0]
    water_depth_max = conditions[1]
    flow_v_min = conditions[2] 
    flow_v_max = conditions [3]
    condition = (water_d >= water_depth_min) & (water_d <= water_depth_max) & (flow_v<=flow_v_max) & (flow_v >= flow_v_min)
    boolean_ar = np.where(condition, 1,0)
    boolean_prop = boolean_ar [np.newaxis,:,:]
    
    return boolean_prop

