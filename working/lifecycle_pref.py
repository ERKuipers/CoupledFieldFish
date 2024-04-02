import campo
import pcraster as pcr 
from op_fields import new_property_from_property, spatial_operation_one_argument
import numpy as np 

def swimmable (self, waterdepth, flow_velocity, prop_name):
    '''
    field waterdepth and field_flow velocity should have the same size
    ''' 
    swimmable = new_property_from_property (prop_name, waterdepth, 0.0)
    #connected_swimmable = _new_property_from_property (waterdepth, 0.0)
    self.water.area.deep_enough = waterdepth >= 0.1 #.30 
    self.water.area.not_drowning = waterdepth <= 1 # should be 0.4
    self.water.area.not_drifting = flow_velocity <= 0.5# should be 0.5
    self.water.area.rheophilic = flow_velocity >= 0.05 #.35 
    self.water.area.spawning_true = self.water.area.deep_enough*self.water.area.not_drowning*self.water.area.not_drifting*self.water.area.rheophilic
    self.water.area.true = 1
    self.water.area.false = 0
    swimmable = campo.where (self.water.area.spawning_true, self.water.area.true, self.water.area.false)
    return swimmable 

def campo_clump (self,boolean_fieldprop):
    connected_boolean = spatial_operation_one_argument('new_prop_from_prop', boolean_fieldprop, pcr.clump, pcr.Boolean)
    # overruling value 0 for areas that are not connected to the big 'non-swimmable land' but are still non-swimmable ! 
    # value 0 for any clump which is non-swimmable  
    connected_boolean_ar = np.where (boolean_fieldprop.values()[0] == 0, 0, connected_boolean.values()[0])  
    connected_boolean_prop = connected_boolean_ar [np.newaxis,:,:]
    return connected_boolean_prop

def connected_swimmable (self, waterdepth, flow_velocity, prop_name):
    swimmable_boolean = swimmable (self, waterdepth, flow_velocity, 'swimmable_boolean')
    connected_swimmable = campo_clump (self, swimmable_boolean, prop_name)
    return connected_swimmable


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

