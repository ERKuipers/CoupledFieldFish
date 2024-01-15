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

def spawning (waterdepth, flow_velocity):
    ''' check if spawning is possible, returns True for spawning possible, False when not possible
    - must be old enough 
    - must be near other barbel --> check another time 
    - must be at spawning suitable grounds ''' 
    if waterdepth > 0.30 and waterdepth <0.40 and flow_velocity >0.35 and flow_velocity <0.5: 
        spawning_possible == True 
    else: 
        spawning_possible == False 
    return spawning_possible 

def closest_spawngrounds (location):
    return closest_spawngrounds
def windowsize (age, flow_velocity): 
    ''' we do windowsize since the fish is apparantly good at hearing and can therefore predict where it would go even on larger distances, but it is still restricted by its swimming speed, of course''' 
    return windowsize 


