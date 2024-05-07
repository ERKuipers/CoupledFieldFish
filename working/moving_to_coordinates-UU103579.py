import numpy as np
import random 
from pathlib import Path 
import sys
in_dir = Path.cwd()
up_dir = in_dir.parent
working = up_dir / 'working'
sys.path.append(f'{working}')
from lookup import raster_values_to_feature, zonal_values_to_feature
from generate_mask import generate_mask
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
    # need to flip again because when calculating with this map points have different orientation than field (see rerasterize)
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


def find_closest_dest (field_pset, boolean_fieldprop, point_pset_orX, pidx_orY): 
    ''' find closest point complying to the boolean fieldprop, from a point
    if point_pset and pidx is inavailable, point_pset may be a xcoordinate  and pidx may be the ycoordinate 
    of the point of which a new destination needs to be found
    parameters: 
        boolean_fieldprop: a boolean map, either as a field-agent property or as a numpy array, describing with 1s the destination
        poi'''
    if isinstance(point_pset_orX, campo.propertyset.PropertySet): 
        point_x = point_pset_orX.space_domain.xcoord [pidx_orY]
        point_y = point_pset_orX.space_domain.ycoord [pidx_orY]
    elif isinstance (point_pset_orX, (np.int64, int, np.float64, float)):
        point_x = point_pset_orX
        point_y = pidx_orY
    else: 
        raise TypeError('make sure third and fourth argument give enough information to substract coordinates, by being a propertyset or integers describing coordinates')
    
    for fidx,area in enumerate(field_pset.space_domain):
      # Get bounding box of field
      nr_cols = int(area[5]) # 
      minX = area [0]
      minY = area [1]
      resolution =  math.fabs(area[2] - minX) / nr_cols

    ix = math.floor((point_x - minX) / resolution) # needs to be rouned down since we define it by the minimum and therefore lower border
    iy = math.floor((point_y - minY) / resolution)
    point = np.array([iy, ix]) # in indexes as in the field , with first row = y, column = x 
    
    # field proerty may be of type property or the values of such a property
    if isinstance (boolean_fieldprop, campo.property.Property):
        field_array = np.flip(boolean_fieldprop.values()[0])
        
    elif isinstance (boolean_fieldprop, np.ndarray): 
        field_array = np.flip (boolean_fieldprop, axis=0)
    else: 
        raise TypeError ('boolean_fieldprop needs to be of type campo.property or of a numpy array with same dimensions as field property values')
    boolean_array = np.where (field_array == 0, 0, 1) # in case it was not boolean yet 
    # Generate a list with all potential destinations, also accommodates for a clump field in which all possible destinations are not 0
    potential_dest_idxs = np.argwhere (boolean_array)
    
    # Convert indices to a 2D array of points 
    # Use NearestNeighbors to find the closest '1' 
    nbrs = NearestNeighbors (n_neighbors= 1, algorithm='ball_tree').fit(potential_dest_idxs)
    distances, indices = nbrs.kneighbors([point]) 
    # these indices are based on the flipped point, so the terugvertaling naar punt gaat dan niet meer, omdat het nu dus een geflipt punt is 
    # the flip operation however has to be performed, otherwise the topological relation is not correctly established 
    new_yidx, new_xidx= tuple(potential_dest_idxs[indices[0][0]]) # but now what do these indices mean on the non flipped array 
    xcoord = new_xidx*resolution + minX 
    ycoord = new_yidx*resolution + minY
    travel_distance = float(distances [0][0])*resolution 
    return xcoord, ycoord, travel_distance

def move_directed (field_pset, dest_boolean_fieldprop, boolean_clump_fieldprop, point_pset, pidx):
    '''boolean_clump_fieldprop = the current clump as a boolean map (is all available area for the current location of the )'''
    # Find closest spawning area pixel destination 
    closest_destX, closest_destY, dist1 = find_closest_dest(field_pset, dest_boolean_fieldprop, point_pset, pidx)
    # from this pixel, find closest clump pixel , which will be in the right direction 
    xcoord, ycoord, dist2 = find_closest_dest(field_pset, boolean_clump_fieldprop, closest_destX, closest_destY)
    initialX = point_pset.space_domain.xcoord[pidx]
    initialY = point_pset.space_domain.xcoord[pidx]
    travel_distance = np.sqrt((xcoord - initialX)**2 +(ycoord - initialY)**2)
    return xcoord, ycoord, travel_distance


def move (self, clump_fieldprop, boolean_fieldprop, dest_fieldprop, point_pset, field_pset, nragents, timestep, has_spawned_pointprop, radius):
    '''Moving to a place which is connected to the initial location of the agent by allowing potential destinations
    
    self: the object class of the model 
    clump_fieldprop: a field agent property describing certain clumps as defined by the pcraster function 'clump'; each clump having a unique ID
    boolean_fieldprop: relates to the location in which the connection is defined. A boolean map which allows for proper connection: this can be a place 
    that can be bridged, like the swimmable or walkable area
    dest_fieldprop: a boolean map relating to possible destinations, for instance: spawning grounds. May be filled in with 'True' / '1'  or can be 
    removed if all destinations are accepted
    point_pset : the  property set of the points to be moved 
    '''
    for fidx, area in enumerate (field_pset.space_domain): 
        nr_cols = int(area[5])
        xmin = area [0]
        ymin = area [1] 
        resolution = math.fabs (area[2] - xmin)/nr_cols # adjust if resolution is different for x and y, then this is the x-resolution 

    agent_clumpID = raster_values_to_feature (point_pset, field_pset, clump_fieldprop) # property describing the clump ID where the agent is 
    xcoords = np.zeros ((nragents))
    ycoords = np.zeros ((nragents))
    available_area = np.zeros((nragents))
    travel_distances = np.zeros ((nragents))
    movemode = np.zeros ((nragents))
    spawns = np.hstack(list(has_spawned_pointprop.values().values.values())) # creating an numpy array while using the property values
    available_pix = zonal_values_to_feature (point_pset, field_pset, clump_fieldprop, dest_fieldprop, 'sum')

    # this needs to be implemented from the fieldprop so that it does not get overwritten by a 0 value in a next timestep
    for pidx, ID in enumerate (agent_clumpID.values()):
        mask = generate_mask (point_pset, pidx, field_pset, radius)
        fieldprop_boolean_value = np.where (clump_fieldprop.values()[0] == ID, 1, 0)
        reachable_array = np.multiply (fieldprop_boolean_value, mask) # reachable within clump
        array_dest = dest_fieldprop.values()[0]
        prob_destination = np.multiply (reachable_array, array_dest) 
        available_area [pidx] = np.sum(prob_destination)*(resolution**2)
        
        # reachable and swimmable within buffer, not taking into account own clump: 
        
        # Make float out of the single value array
        if timestep == 1: # first moving the 
            xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, clump_fieldprop, resolution, xmin, ymin, 1)
            xcoords [pidx] = xcoord_array.item()
            ycoords [pidx] = ycoord_array.item()
   
        elif ID == 0: # on non-swimmable area, just the closest piece of swimmable area 
            # find the closest non-dry land to go to 
            masked_swimmable = np.multiply(boolean_fieldprop.values()[0], 1)
            xcoords [pidx], ycoords [pidx], travel_distances [pidx] = find_closest_dest (field_pset, masked_swimmable, point_pset, pidx)
            movemode [pidx] = 2 # nearest destination 
            print (f'I, {pidx}, am dryswimming! help me get back')
        elif has_spawned_pointprop.values()[pidx]==1:
            xcoords [pidx] = xmin # moving spawners to the corner !! 
            ycoords [pidx] = ymin
            # writing the available area so that also when spawning, the available area can be printed 
            movemode [pidx]= 1 # random displacement within clump
            print (f'been there, done that (the spawning), {pidx} out')
        else: 
            # the available area per barbel in unit^2 as in the data 
            # if theres no spawning in proximate area, move in the direction of the closest
            if available_area[pidx] == 0: # has not spawned yet but no available area within clump and 20 km
                masked_swimmable = np.multiply(boolean_fieldprop.values()[0], mask)
                xcoords [pidx], ycoords [pidx], travel_distances [pidx] = move_directed (field_pset, dest_fieldprop, masked_swimmable, point_pset, pidx)
                movemode [pidx] = 3 # directed move
                print (f'I {pidx} rate the spawning availability over here 0/5 stars')
            else: # spawning:
                # generating destination maps, moving there
                xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, prob_destination, resolution, xmin, ymin, 1)
                xcoords [pidx] = xcoord_array.item()
                ycoords [pidx] = ycoord_array.item()
                travel_distances [pidx] = np.sqrt ((point_pset.space_domain.xcoord[pidx]-xcoords[pidx])**2 + (point_pset.space_domain.ycoord[pidx]-ycoords[pidx])**2)
                spawns [pidx] = 1
                movemode [pidx]= 4 # destination oriented 
                print (f'dope ! #sex {pidx}')
    return xcoords, ycoords, available_area, travel_distances, spawns, movemode

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
    spawns = np.hstack(list(has_spawned_pointprop.values().values.values())) # creating an numpy array while using the property values
    print ((spawns)) # this needs to be implemented from the fieldprop so that it does not get overwritten by a 0 value in a next timestep
    for pidx, value_array in enumerate (agent_clumpID.values()):
        # Make float out of the single value array
        value = value_array.item()
        fieldprop_boolean_value = np.where (clump_fieldprop.values()[0] == value, 1, 0)  
        # Being sweet for beginner agents: 
        # Making sure that for the first timestep, the agent get placed in a proper boolean field :), 
        # Using the function coordinatelist_to_fieldloc one agent at a time, so that the agent is placed in the 
        if timestep == 1: # first moving the 
            xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, boolean_fieldprop, resolution, xmin, ymin, 1)
            xcoords [pidx] = xcoord_array.item()
            ycoords [pidx] = ycoord_array.item()

        elif value == 0: # on non-swimmable no destination to go to, just the closest piece of swimmable area 
            # find the closest non-dry land to go to 
            xcoords [pidx], ycoords [pidx], travel_distances [pidx] = find_closest_dest (self, boolean_fieldprop, point_pset, pidx, xmin, ymin, resolution)  
            print (f'i, {pidx}, am dryswimming! help me get back')
        elif has_spawned_pointprop.values()[pidx]==1:
            xcoord_array, ycoord_array = coordinatelist_to_fieldloc (self, fieldprop_boolean_value, resolution, xmin, ymin, 1)
            xcoords [pidx] = xcoord_array.item()
            ycoords [pidx] = ycoord_array.item()
            # writing the available area so that also when spawning, the available area can be printed 
            array_dest = dest_fieldprop.values()[0]
            prob_destination = np.multiply (fieldprop_boolean_value, array_dest)
            available_pix = (len(np.argwhere (prob_destination)))
            available_area [pidx] = available_pix*(resolution**2) # still writing the available area 
            print (f'been there, done that (the spawning), {pidx} out')
        else: 
            array_dest = dest_fieldprop.values()[0]
            prob_destination = np.multiply (fieldprop_boolean_value, array_dest)
            available_pix = (len(np.argwhere (prob_destination)))
                # the available area per barbel in unit^2 as in the data 
            # if theres no spawning in proximate area, move in the direction of the closest
            if available_pix == 0: # has not spawned yet but no available area
                xcoords [pidx], ycoords [pidx], travel_distances [pidx] = move_directed (self, dest_fieldprop, fieldprop_boolean_value, point_pset, pidx, xmin, ymin, resolution)
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
