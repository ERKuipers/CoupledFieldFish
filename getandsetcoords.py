

def getandsetcoords (self):
    #### get the coordinates for each agent #### getting the x_coordinates (wow this is so intuitive im impressed)
    # for a specific property set # 
    self.bullsxcoords = self.bulls.char._space_domain.xcoord
    self.bullsycoords = self.bulls.char._space_domain.ycoord 
    ## alter the coordinates 
    alteredxcoords = self.bullsxcoords + 10 * self.timestep 
    alteredycoords = self.bullsycoords + 10 * self.timestep
    # set them to the space domain 
    self.bulls.char._space_domain.xcoord = alteredxcoords 
    self.bulls.char._space_domain.ycoord = alteredycoords

    # optional writing to a csv, import csv 
    # coords_file = 'bulls_coordinates' + str(self.i) +  '.csv'
    # with open (str(coords_file), 'w', newline = '') as csvfile:
    #     filewriter = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_NONNUMERIC)
    #     for x,y in zip (self.bullsxcoords, self.bullsycoords): 
    #         filewriter.writerow ([x,y])
    