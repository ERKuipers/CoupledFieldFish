import numpy as np
import math
import matplotlib.pyplot as plt
def generate_mask (point_pset, pidx, field_pset, radius):
    '''radius = in unit of model, so probably metres '''

  # Loop over space attributes of the different points in the point agents propertyset
    point_x = point_pset.space_domain.xcoord[pidx]
    point_y = point_pset.space_domain.ycoord[pidx]

    for fidx,area in enumerate(field_pset.space_domain):
    # Get bounding box of field
        nr_rows = int(area[4])
        nr_cols = int(area[5]) # 
        minX = area [0]
        minY = area [1] 
        
        # Translate point coordinate to index on the field array
        cellsize = math.fabs(area[2] - minX) / nr_cols # in unit of length 
        ix = math.floor((point_x - minX) / cellsize) 
        iy = math.floor((point_y - minY) / cellsize) 
    
    
    mask_unflipped = np.zeros((nr_rows, nr_cols))  # Initialize mask with NaN

    # Generate grid of coordinates
    x, y = np.meshgrid(np.arange(nr_cols), np.arange(nr_rows))

    # Calculate distance from each point to the center
    distance = np.sqrt((x - ix)**2 + (y - iy)**2)
    # Convert model unit to number of cells 
    cell_radius = math.floor(radius / cellsize)
    # Set values inside the radius to 1
    mask_unflipped[distance <= cell_radius] = 1
    mask = np.flip (mask_unflipped, axis=0)
    return mask