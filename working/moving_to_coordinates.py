import numpy as np
import random 
from lookup import raster_values_to_feature
from op_fields import new_property_from_property
import campo

def coordinatelist_to_fieldloc (self, fieldcondition_prop, point_propset, resolution, xmin, ymin, nragents):
    
    '''
    - fieldcondition_prop = a property that is a field and contains true values for places where an agent may move to   
    - point_propset = the property set that has the move (=point agents)
    - xmin = minimal extent of the field 
    - ymin = maximum extent of the field 
    - nragents = the number of point agents 
    return lists of coordinates with the same length as the number of agents in a point propertyset (sueful wehn you want to make them move there) 
    '''
    # need to flip again because its at some point also flipped, a bit weird (see rerasterize)
    map_flipped = np.flip (fieldcondition_prop.values()[0], axis=0) 
    # finding the indices of the places where the fieldcondition is true 
    coords_idx = np.argwhere (map_flipped) #coordinates of the spawning grounds in [y,x]
    # collecting the coordinate combination in a tuple so as to prevent them from being 'disconnected' from eachother 
    coords_list = [tuple(row) for row in coords_idx] 
    random_newindex = random.sample (coords_list, nragents) # nr of agents is the subsetsize
    # seperating the tuples in the list in two seperate list
    yindex, xindex = zip(*random_newindex) #assuming that tuple list is reversed, first gives y then x as in column = x and row = y 
    xindex = np.array (xindex)
    yindex = np.array (yindex)
    xcoords = np.zeros(nragents)
    ycoords = np.zeros(nragents)

    # make from x index a x coordinate by using resolution and bounding box information
    for i, xvalue in enumerate(xindex):
        xcoords [i] = (xvalue*resolution + xmin) 
    for j, yvalue in enumerate(yindex): 
        ycoords[j] = (yvalue *resolution + ymin)
    
    
    #xcoords = [(xvalue * resolution + xmin) for xvalue in xindex]
    # print (xcoords) # zijn nog steeds de indexen 
    # ycoords = [(yvalue * resolution + ymin) for yvalue in yindex]
    
    return xcoords, ycoords 

def connected_move (self, clump_fieldprop, point_pset, field_pset, resolution, xmin, ymin, nragents):
    '''moving to a place which is connected to the initial location of the agent by allowing potential destinations
    to be part '''

    agent_clumpID = raster_values_to_feature (point_pset, field_pset, clump_fieldprop) # property describing the clump ID where the agent is 
    xcoords = np.zeros ((nragents))
    ycoords = np.zeros ((nragents))
    for pidx, value_array in enumerate (agent_clumpID.values()): 
        self.water.area.true_prop = 1 # new_property_from_property('True', clump_fieldprop, 1)
        self.water.area.false_prop = 0 # new_property_from_
        value = value_array.item() # make float out of the single value array 
        fieldprop_boolean_value = campo.where (clump_fieldprop == value, self.water.area.true_prop, self.water.area.false_prop)
        map_flipped = np.flip (fieldprop_boolean_value.values()[0], axis=0)
        coords_idx = np.argwhere (map_flipped)
        coords_list = [tuple(row) for row in coords_idx]   # coordinates of the suitable places in [y,x]
        random_single_destination = random.sample (coords_list, 1) # list with something in it ? 
        yidx, xidx = random_single_destination[0]
        xcoords[pidx] = xidx * resolution + xmin 
        ycoords [pidx] = yidx*resolution + ymin
    return xcoords, ycoords 