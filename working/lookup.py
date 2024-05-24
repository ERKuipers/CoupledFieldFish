'''

'''
from osgeo import gdal
from osgeo import osr
from osgeo import ogr

gdal.UseExceptions()

import math
import numpy as np

from campo.points import Points
from campo.areas import Areas
from campo.property import Property


def raster_values_to_feature(point_pset, field_pset, field_prop):
  ''' Queries the raster values of one field property on the location of point agents, 
  writes this as a new point agent property set 
  Parameters:
    point_pset: property set of the point agents to be attributed the location 
    field_pset: property set of a single field 
    field_prop: property of which the values are attributed to the newly generated point property
  Returns: 
    point_prop: property of point agents with values of local field values'''
  
  # generate empty point property given point property space definitions
  point_prop = Property('emptycreatename', point_pset.uuid, point_pset.space_domain, point_pset.shapes)
  
  # loop over space attributes of the different points in the point agents propertyset
  for pidx,coordinate in enumerate(point_pset.space_domain):
    point_x = point_pset.space_domain.xcoord[pidx]
    point_y = point_pset.space_domain.ycoord[pidx]

    point_value = np.zeros(1)  
    for fidx,area in enumerate(field_pset.space_domain):

      # get bounding box of field
      nr_cols = int(area[5]) # 
      minX = area [0]
      minY = area [1] 
      
      # translate point coordinate to index on the field array
      cellsize = math.fabs(area[2] - minX) / nr_cols 
      ix = math.floor((point_x - minX) / cellsize) 
      iy = math.floor((point_y - minY) / cellsize) 
      
      # reshape property to a mirrored numpy field array to accommodate right use of point and agent indexes 
      reshaped = np.flip (field_prop.values()[fidx], axis=0) 
      # query the field attribute given point location
      point_value[fidx] = reshaped[iy,ix] 

    # write the value to the point property for each point agent
    point_prop.values()[pidx] = point_value.item() 

  return point_prop

def window_values_to_feature(point_pset, field_pset, field_prop, windowsize, operation):
  ''' Queries aggregative raster values of a window of a field property based from the location of point agents, 
  Given a certain aggregative operation. Writes this as a new point agent property. 
  Parameters:
    point_pset: property set of the point agents to be attributed the location 
    field_pset: property set of a single field 
    field_prop: property of which the values are attributed to the newly generated point property
    windowsize: we make square windows: windowsize describes the length of the window in the unit of the field_property
    operation: aggregative numpy operation as a string ('sum', 'mean', 'min', 'max', 'etc')
  Returns: 
    point_prop: property of point agents with values of aggregated field values'''
  
  # Generate operator, first checking if operation is available in numpy
  if not hasattr (np, operation):
    raise ValueError (f'Unsupported numpy operation, {operation}')
  operator = getattr(np, operation)

  # Generate empty point property given point property space definitions
  point_prop = Property('emptycreatename', point_pset.uuid, point_pset.space_domain, point_pset.shapes)
  # Loop over space attributes of the different points in the point agents propertyset
  for pidx,coordinate in enumerate(point_pset.space_domain):
    point_x = point_pset.space_domain.xcoord[pidx]
    point_y = point_pset.space_domain.ycoord[pidx]

    window_value = np.zeros(1)  
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
      
      nr_windowcells = math.floor(windowsize/cellsize)

      ws_iy = math.floor(iy - 0.5*nr_windowcells) 
      we_iy = math.floor(iy + 0.5*nr_windowcells)
      ws_ix = math.floor (ix - 0.5*nr_windowcells)
      we_ix = math.floor (ix + 0.5*nr_windowcells)
      # Reshape field property to a mirrored numpy field array to accommodate right use of point and agent indexes 
      reshaped = np.flip (field_prop.values()[fidx], axis=0) 
      
      # Query the field attribute given point location
      window_value[fidx] = operator (reshaped [ws_iy:we_iy, ws_ix:we_ix])
    
    # Write the value to the point property for each point agent
    point_prop.values()[pidx] = window_value.item() 

  return point_prop

def zonal_values_to_feature(point_pset, field_pset, field_prop_class, field_prop_var, operation):
  ''' Queries aggregative raster values of a zone of a field property based on the location
    of point agents within a classification map, given a certain aggregative operation. 
    Writes this as a new point agent property. Only works for one fieldagent existing at the location. 
    Fieldagents with overlapping domains cannot generate an output
    E.g.: According to both the agent's location and a soil map (field_prop_class), the agent is positioned in 
        soil '2' , which is clay. With the operation 'mean', the mean rainfall (from field_prop_var) 
        is calculated and attributed to the agent
  Parameters:
    point_pset: property set of the point agents to be attributed the location 
    field_pset: property set of a single field 
    field_prop_class: property describing classes or groups of cells of which the zonal extent shall be the windowsize of the aggregration
    field_prop_var: property describing the variable which needs to be aggregated,
      in case of a boolean map, 'True' values are 1
    operation: operation: aggregative numpy operation as a string ('sum', 'mean', 'min', 'max', 'etc')
  Returns: 
    point_prop: property of point agents with values of aggregated field values'''
  
  # Generate operator, first checking if operation is available in numpy
  if not hasattr (np, operation):
    raise ValueError (f'Unsupported numpy operation, {operation}')
  operator = getattr(np, operation)

  # Identifying the zone the agent is in
  agents_zoneIDs = raster_values_to_feature(point_pset,field_pset, field_prop_class)
  # Generate empty point property given point property space definitions
  point_prop = Property('emptycreatename', point_pset.uuid, point_pset.space_domain, point_pset.shapes)
  # make as many field properties as there are agents:  
  # Loop over space attributes of the different points in the point agents propertyset
  for pidx, ID in enumerate(agents_zoneIDs.values()):
    # Making a boolean map concerning the extent of the zone for each agent
    aggr_zone_var = np.zeros(1)
    for fidx,area in enumerate(field_pset.space_domain):
        zone_extent = np.where (field_prop_class.values()[fidx] == ID, 1, 0)
        variable_zone_array = np.multiply (zone_extent, field_prop_var.values()[fidx])
        # we don't need to flip this time, since the raster_values_to_feature already gave 
        # the right topological relationship between the field and the agent: 
        # the zone_extent array describes the zone in which the agent is positioned. 
        # This array might be flipped, but this won't lead to any different outcomes of aggregative operations
        aggr_zone_var[fidx] = operator (variable_zone_array)
    #field_prop_array [pidx] = field_prop# array as long as the number of agents filled with a field prop for each agent
    # Write the value to the point property for each point agent
    point_prop.values()[pidx] = aggr_zone_var.item() 
    
  return point_prop

# could potentially add mask to make it suitable for reuse 