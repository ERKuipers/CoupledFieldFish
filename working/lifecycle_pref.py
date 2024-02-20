import campo

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

def spawning (self, waterdepth, flow_velocity):
    ''' check if spawning is possible, returns True for spawning possible, False when not possible
    - must be old enough 
    - must be near other barbel --> check another time 
    - must be at spawning suitable grounds ''' 
    if waterdepth > 0.30 and waterdepth <0.40 and flow_velocity >0.35 and flow_velocity <0.5: 
        spawning_possible = 1
    else: 
        spawning_possible = 0
    return spawning_possible 

def closest_spawngrounds (location):
    return closest_spawngrounds
def windowsize (age, flow_velocity): 
    ''' we do windowsize since the fish is apparantly good at hearing and can therefore predict where it would go even on larger distances, but it is still restricted by its swimming speed, of course''' 
    return windowsize 



def spawning_true (self, water_depth, flow_velocity ):

    self.water.area.deep_enough = water_depth >= 0 #.30 
    self.water.area.not_drowning = water_depth <= 1 # should be 0.4
    self.water.area.not_drifting = flow_velocity <= 1 # should be 0.5
    self.water.area.rheophilic = flow_velocity >= 0 #.35 
    self.water.area.spawning_true = self.water.area.deep_enough*self.water.area.not_drowning*self.water.area.not_drifting*self.water.area.rheophilic
    self.water.area.true = 1
    self.water.area.false = 0
    self.water.area.spawning_grounds = campo.where (self.water.area.spawning_true, self.water.area.true, self.water.area.false)
    return self.water.area.spawning_grounds

