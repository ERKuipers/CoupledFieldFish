import numpy as np
import random 
from lookup import raster_values_to_feature
from op_fields import new_property_from_property
import campo
from sklearn.neighbors import NearestNeighbors
import math

def coordinatelist_to_fieldloc (self, boolean_fieldprop, resolution, xmin, ymin, nragents):
    '''
    - boolean_fieldprop = a property that is a field and contains true values for places where an agent may move to   
    - point_propset = the property set that has the move (=point agents)
    - xmin = minimal extent of the field 
    - ymin = maximum extent of the field 
    - nragents = the number of point agents 
    return lists of coordinates with the same length as the number of agents in a point propertyset (sueful wehn you want to make them move there) 
    '''
    # need to flip again because its at some point also flipped, a bit weird (see rerasterize)
    if isinstance(boolean_fieldprop, np.ndarray):
        map_flipped = np.flip (boolean_fieldprop, axis=0)
    elif isinstance (boolean_fieldprop, campo.property.Property):
        map_flipped = np.flip (boolean_fieldprop.values()[0], axis=0) 
    else:
        raise TypeError ('boolean_fieldprop needs to be of type campo.property or of a numpy array with same dimensions as field property values')
    
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


def find_closest_dest (self, boolean_fieldprop, point_pset_orX, pidx_orY, minX, minY, resolution): 
    ''' find closest point complying to the boolean fieldprop, from a point
    if point_pset and pidx is inavailable, point_pset may be a xcoordinate  and pidx may be the ycoordinate 
    of the point of which a new destination needs to be found
    parameters: 
        boolean_fieldprop: a boolean map, either as a field-agent property or as a numpy array, describing with 1s the destination
        poi'''
    if isinstance(point_pset_orX, campo.propertyset.PropertySet): 
        point_x = point_pset_orX.space_domain.xcoord [pidx_orY]
        point_y = point_pset_orX.space_domain.ycoord [pidx_orY]
    elif isinstance (point_pset_orX, (np.int64, int)):
        point_x = point_pset_orX
        point_y = pidx_orY
    else: 
        raise TypeError('make sure third and fourth argument give enough information to substract coordinates, by being a propertyset or integers describing coordinates')
    
    ix = math.floor((point_x - minX) / resolution) # needs to be rouned down since we define it by the minimum and therefore lower border
    iy = math.floor((point_y - minY) / resolution)
    point = np.array([iy, ix]) # in indexes as in the field , with first row = y, column = x 
    
    # field proerty may be of type property or the values of such a property
    if isinstance (boolean_fieldprop, campo.property.Property):
        boolean_array = np.flip(boolean_fieldprop.values()[0])
    elif isinstance (boolean_fieldprop, np.ndarray): 
        boolean_array = np.flip (boolean_fieldprop, axis=0)
    else: 
        raise TypeError ('boolean_fieldprop needs to be of type campo.property or of a numpy array with same dimensions as field property values')
    
    # Generate a list with all potential destinations, also accommodates for a clump field in which all possible destinations are not 0
    potential_dest_idxs = np.where (boolean_array != 0) 
    # Convert indices to a 2D array of points 
    pot_dest_points = np.column_stack(potential_dest_idxs) 

    # Use NearestNeighbors to find the closest '1' 
    nbrs = NearestNeighbors (n_neighbors= 1, algorithm='ball_tree').fit(pot_dest_points)
    distances, indices = nbrs.kneighbors([point]) 
    new_yidx, new_xidx= tuple(pot_dest_points[indices[0][0]])
    xcoord = new_xidx* resolution + minX
    ycoord = new_yidx* resolution + minY
    travel_distance = float(distances [0][0])*resolution
    return xcoord, ycoord, travel_distance

def move_directed_border (self, dest_boolean_fieldprop, boolean_clump_fieldprop, point_pset, pidx, minX, minY, resolution):
    '''boolean_clump_fieldprop = the current clump as a boolean map (is all available area for the current location of the )'''
    # Find closest spawning area pixel destination 
    closest_destX, closest_destY, dist1 = find_closest_dest(self, dest_boolean_fieldprop, point_pset, pidx, minX, minY, resolution)
    # from this pixel, find closest clump pixel , which will be in the right direction 
    xcoord, ycoord, dist2 = find_closest_dest(self, boolean_clump_fieldprop, closest_destX, closest_destY, minX, minY, resolution)
    initialX = point_pset.space_domain.xcoord[pidx]
    initialY = point_pset.space_domain.xcoord[pidx]
    travel_distance = np.sqrt((xcoord - initialX)**2 +(ycoord - initialY)**2)
    return xcoord, ycoord, travel_distance

def connected_move (self, clump_fieldprop, boolean_fieldprop, dest_fieldprop, point_pset, field_pset, resolution, xmin, ymin, nragents, timestep, has_spawned_pointprop):
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
    travel_distances = np.zeros ((nragents))
    spawns = has_spawned_pointprop.values() # this needs to be implemented from the fieldprop so that it does not get overwritten by a 0 value in a next timestep
    for pidx, value_array in enumerate (agent_clumpID.values()):
        # Make float out of the single value array
        value = value_array.item()   
        # Being sweet for beginner agents: 
        # Making sure that for the first timestep, the agent get placed in a proper boolean field :), 
        # Using the function coordinatelist_to_fieldloc one agent at a time, so that the agent is placed in the 
        
        if timestep == 1: # first moving the 
            xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, boolean_fieldprop, resolution, xmin, ymin, 1)
            xcoords [pidx] = xcoord_array.item()
            ycoords [pidx] = ycoord_array.item()
 
        elif value == 0: # on non-swimmable no destination to go to, just the closest piece of swimmable area 
            # find the closest non-dry land to go to 
            xcoords [pidx], ycoords [pidx], travel_distances [pidx] = find_closest_dest (self, clump_fieldprop, point_pset, pidx, xmin, ymin, resolution)  
            print (f'i, {pidx}, am dryswimming! help me get back')
            # no more searching for spawning ! 
        else:
            fieldprop_boolean_value = np.where (clump_fieldprop.values()[0] == value, 1, 0)
            # barbels only spawn once a season , else random placement within their clump (maybe death? :0)
            if has_spawned_pointprop.values()[pidx]==1: #is true
                xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, fieldprop_boolean_value, resolution, xmin, ymin, 1)
                xcoords [pidx] = xcoord_array.item()
                ycoords [pidx] = ycoord_array.item()
                print (f'been there, done that (the spawning), {pidx} out')
            else: 
                array_dest = dest_fieldprop.values()[0]
                prob_destination = np.multiply (fieldprop_boolean_value, array_dest)
                available_pix = (len(np.argwhere (prob_destination)))
                 # the available area per barbel in unit^2 as in the data 
                # if theres no spawning in proximate area, move in the direction of the closest
                if available_pix == 0: # has not spawned yet but no available area
                    xcoords [pidx], ycoords [pidx], travel_distances [pidx] = move_directed_border (self, dest_fieldprop, fieldprop_boolean_value, point_pset, pidx, xmin, ymin, resolution)
                    print (f'I {pidx} rate the spawning availability over here 0/5 stars')
                else: # spawning: 
                    xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, prob_destination, resolution, xmin, ymin, 1)
                    xcoords [pidx] = xcoord_array.item()
                    ycoords [pidx] = ycoord_array.item()
                    available_area [pidx] = available_pix*(resolution**2)
                    travel_distances [pidx] = np.sqrt ((point_pset.space_domain.xcoord[pidx]-xcoords[pidx])**2 + (point_pset.space_domain.ycoord[pidx]-ycoords[pidx])**2)
                    spawns [pidx] = 1
                    print (f'dope ! #sex {pidx}')

    return xcoords, ycoords, available_area, travel_distances, spawns 

def connected_move1 (self, clump_fieldprop,boolean_fieldprop, dest_fieldprop, point_pset, field_pset, resolution, xmin, ymin, nragents, timestep, has_spawned_pointprop):
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
    return xcoords, ycoords, 0, 0 , 0