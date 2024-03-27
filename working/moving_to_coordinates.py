import numpy as np
import random 
from lookup import raster_values_to_feature
from op_fields import new_property_from_property
import campo

def coordinatelist_to_fieldloc (self, boolean_fieldprop, point_propset, resolution, xmin, ymin, nragents):
    '''
    - boolean_fieldprop = a property that is a field and contains true values for places where an agent may move to   
    - point_propset = the property set that has the move (=point agents)
    - xmin = minimal extent of the field 
    - ymin = maximum extent of the field 
    - nragents = the number of point agents 
    return lists of coordinates with the same length as the number of agents in a point propertyset (sueful wehn you want to make them move there) 
    '''
    # need to flip again because its at some point also flipped, a bit weird (see rerasterize)
    map_flipped = np.flip (boolean_fieldprop.values()[0], axis=0) 
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
    return xcoords, ycoords 


def connected_move (self, clump_fieldprop, boolean_fieldprop, dest_fieldprop, point_pset, field_pset, resolution, xmin, ymin, nragents, timestep):
    '''Moving to a place which is connected to the initial location of the agent by allowing potential destinations
    to be part 
    self: the object class of the model 
    clump_fieldprop: a field agent property describing certain clumps as defined by the pcraster function 'clump'; each clump having a unique ID
    boolean_fieldprop: relates to the location in which the connection is defined. A boolean map which allows for proper connection: this can be a place 
    that can be bridged, like the swimmable or walkable area
    dest_fieldprop: a boolean map relating to possible destinations, for instance: spawning grounds. May be filled in with 'True' / '1'  or can be 
    removed if all destinations are accepted
    point_pset : the  property set of the points to be moved 
    '''

    agent_clumpID = raster_values_to_feature (point_pset, field_pset, clump_fieldprop) # property describing the clump ID where the agent is 
    xcoords = np.zeros ((nragents))
    ycoords = np.zeros ((nragents))
    available_area = np.zeros((nragents))
    for pidx, value_array in enumerate (agent_clumpID.values()):
        # make float out of the single value array
        value = value_array.item()   
        # being sweet for beginner agents: 
        # making sure that for the first timestep, the agent get placed in a proper boolean field :), 
        # using the function coordinatelist_to_fieldloc one agent at a time, so that the agent is placed in the 

        if timestep == 1 and value == 1: 
            xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, boolean_fieldprop, point_pset, resolution, xmin, ymin, 1)
            xcoords [pidx] = xcoord_array.item()
            ycoords [pidx] = ycoord_array.item()
        # elif value==1: 
        # find closest =!1 
        else:
            fieldprop_boolean_value = np.where (clump_fieldprop.values()[0] == value, 1, 0)
            array_dest = dest_fieldprop.values()[0]
            prob_destination = np.multiply (fieldprop_boolean_value, array_dest)
            map_flipped = np.flip (prob_destination, axis=0)
            coords_idx = np.argwhere (map_flipped)
            available_pix = len(coords_idx)
            available_area [pidx] = available_pix*resolution**2 # the available area in unit^2 as in the data 
            print (available_area[pidx])
            # if theres no spawning in proximate area, remain at same place !  
            if available_pix == 0: 
                xcoords [pidx] = point_pset.space_domain.xcoord[pidx]
                ycoords [pidx] = point_pset.space_domain.ycoord[pidx]
            else: 
                coords_list = [tuple(row) for row in coords_idx]  # coordinates of the suitable places in [y,x]
                random_single_destination = random.sample (coords_list, 1) # list with tuple in it 
                yidx, xidx = random_single_destination[0]
                xcoords[pidx] = xidx* resolution + xmin 
                ycoords[pidx] = yidx* resolution + ymin

    return xcoords, ycoords, available_area


