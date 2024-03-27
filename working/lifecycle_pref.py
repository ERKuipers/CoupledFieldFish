import campo
import pcraster as pcr 
from op_fields import new_property_from_property, spatial_operation_one_argument
import numpy as np 


def lifecycle_pref (age): 
    ''' determines preferences based on age '''
    if age < 100: 
        d_pref = [0.3,0.4] #min_depth_m, max
        u_pref = [0.35,0.5]
    elif age < 365: 
        d_pref =  [0.25,0.7]
        u_pref = [0.1, 0.6]
    elif age > 365: 
        d_pref = [0.5,100]
        u_pref = [0.05, 0.5]
    return d_pref, u_pref 

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

def campo_clump (self,boolean_fieldprop, prop_name):
    connected_boolean = spatial_operation_one_argument(prop_name, boolean_fieldprop, pcr.clump, pcr.Boolean)
    #boolean_clump = campo.where (connected_swimmable == 1, self.water.area.false,self.water.area.true)
    #unique_clump = spatial_operation_one_argument (new_prop_name, boolean_clump, pcr.uniqueid, pcr.Boolean)
    return connected_boolean

def connected_swimmable (self, waterdepth, flow_velocity, prop_name):
    swimmable_boolean = swimmable (self, waterdepth, flow_velocity, 'swimmable_boolean')
    connected_swimmable = campo_clump (self, swimmable_boolean, prop_name)
    return connected_swimmable

def spawning (self, waterdepth, flow_velocity):
    ''' check if spawning is possible, returns True for spawning possible, False when not possible
    - must be old enough 
    - must be near other barbel --> check another time 
    - must be at spawning suitable grounds ''' 
    spawning_possible = campo._new_property_from_property ('spawning_possible', waterdepth, 0.0)
    spawning = campo._new_property_from_property ('spawning', waterdepth, 0.0)

    spawning_possible = pcr.pcrand(flow_velocity <0.5,(pcr.pcrand(flow_velocity >0.35,pcr.pcrand(waterdepth > 0.30, waterdepth <0.40))))
    spawning_flow = flow_velocity >0.35 and flow_velocity <0.5
    #true 
    #false
    #spawning_possible = campo.where (spawning, true, false)
    return spawning_possible 

def closest_spawngrounds (location):
    return closest_spawngrounds
def windowsize (age, flow_velocity): 
    ''' we do windowsize since the fish is apparantly good at hearing and can therefore predict where it would go even on larger distances, but it is still restricted by its swimming speed, of course''' 
    return windowsize 


def spawning_true (self, water_depth, flow_velocity ):
    water_d = water_depth.values()[0]
    flow_v = flow_velocity.values()[0]
    condition = (water_d >= 0.30) & (water_d <= 0.4) & (flow_v<=0.5) & (flow_v >=0.35)
    spawning_ar = np.where(condition, 1,0)
    spawning_prop = spawning_ar [np.newaxis,:,:]
    return spawning_prop

