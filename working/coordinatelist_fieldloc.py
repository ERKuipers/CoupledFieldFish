import numpy as np
import random 
def coordinatelist_to_fieldloc (self, fieldcondition_prop, point_propset, resolution, xmin, ymin, nragents):
    
    '''
    - fieldcondition_prop = a property that is a field and contains true values for places where an agent may move to   
    - point_propset = the property set that has the move (=point agents)
    - xmin = minimal extent of the field 
    - ymin = maximum extent of the field 
    - nragents = the number of point agents 
    return lists of coordinates with the same length as the number of agents in a point propertyset (sueful wehn you want to make them move there) 
    '''

    spawncoords = np.argwhere (fieldcondition_prop.values()[0]) #coordinates of the spawning grounds in [x,y]
    
    spawncoords_list = [tuple(row) for row in spawncoords]
    # find the amount of barbel
    subsetsize = nragents # nr of barbel 
    random_newindex = random.sample (spawncoords_list, subsetsize)
    xindex, yindex = zip(*random_newindex)
    xindex = np.array (xindex)
    yindex = np.array (yindex)
    xcoords = np.zeros(nragents)
    ycoords = np.zeros(nragents)
    i=0
    j=0
    for xvalue in xindex:
        xcoords [i] = (xvalue * resolution + xmin)
        i +=1 
    for yvalue in yindex: 
        ycoords[j] = (yvalue * resolution + ymin)
        j +=1 
    
    #xcoords = [(xvalue * resolution + xmin) for xvalue in xindex]
    # print (xcoords) # zijn nog steeds de indexen 
    # ycoords = [(yvalue * resolution + ymin) for yvalue in yindex]
    
    return xcoords, ycoords 