import numpy as np
import random 
def coordinatelist_to_fieldloc (self, fieldcondition_prop, point_propset, resolution, xmin, ymin, nragents):
    ''' return lists of coordinates with the same length as the number of agents in a point propertyset (sueful wehn you want to make them move there) 
    '''

    spawncoords = np.argwhere (fieldcondition_prop.values()[0]) #coordinates of the spawning grounds in [x,y]
    
    spawncoords_list = [tuple(row) for row in spawncoords]
    # find the amount of barbel
    subsetsize = nragents # nr of barbel 
    random_newindex = random.sample (spawncoords_list, subsetsize)
    xindex, yindex = zip(*random_newindex)
    xindex = list (xindex)
    yindex = list (yindex)
    xcoords = []
    ycoords = []
    for xvalue in xindex: 
       xcoords.append(xvalue * resolution + xmin)
    for yvalue in yindex: 
        ycoords.append (yvalue * resolution + ymin)
    
    #xcoords = [(xvalue * resolution + xmin) for xvalue in xindex]
    # print (xcoords) # zijn nog steeds de indexen 
    # ycoords = [(yvalue * resolution + ymin) for yvalue in yindex]
    
    return xcoords, ycoords 