#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tuesday April 26 07:07:54 2016

@author: Joseph

"""

import numpy as np
import matplotlib.pyplot as pyplot
import time
import copy

Xlist = []
XXlist = []
Ylist = []
YYlist = []
Zlist = []
ZZlist = []



# set variable values

ticks = 5 # number of timesteps

grid_x = 175  # total grid length
grid_y = 150 # width of grid
grid_x_slope_length = 150 # length of slope

coverage = 0.15 # % coverage by cryoconite

np.random.seed(0)
grid = np.random.choice(
        [0, 1, 2, 3, 4, 5, 6, 7],
        (grid_x, grid_y), 
        p=[1-coverage, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7]
)
initial_grid = copy.deepcopy(grid)

ticks_per_delivery = 3 # frequency of sediment delivery
delivery_zone = 10 # number of rows populated by sediment delivery

# migration rate for single grain layers (0-1)
singlelayer_speed = 0.3 # probability of movement.
# migration rate for stacked sediment (0-1)
multilayer_speed = 0.7 # probability of movement 
# migration rate for cryoconite on flat ice
flat_speed = 0.2 

drop_zone = 6 # size of 'buffer zone' where cryoconite is discarded off grid

# setup the pyplot environment
pyplot.figure(figsize=(12, 12))
pyplot.imshow(initial_grid, cmap='coolwarm') #Greys
cbar=pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], orientation='horizontal')
pyplot.tick_params(axis='y', direction='out')
pyplot.tick_params(axis='x', direction='out')
#pyplot.savefig('CAmovie0')


# define automaton rules

def cellrules(grid_x_slope_length, grid_x, Idel, del_area, grid_y, coverage, singlelayer_speed, multilayer_speed, flatspeed, dropzone):
    
    # Initialize variables for stats
    cells_with_sediment = 0
    sediment_on_grid = 0

    slope_cells_with_sediment = 0
    sediment_on_slope = 0

    flat_cells_with_sediment = 0
    sediment_on_flat = 0
    
    # for each cell on the slope
    for i in np.arange(0, grid_x_slope_length, 1):
        # TODO: check if this is a bug, 
	# the loop is skips the left-most and rightmost columns, so material can 
	# fall off the side of the grid, but it is not able to re-enter
	#
	# TODO: check if bug that you are not using a buffer.
	# as material moves down the slope, it will be picked up in the next itteration of the grid_x loop.
	# so it is perfectly possible for sediment to be deposited at the top of the slope and traerse the whole slope in one itteration.
	
        for j in np.arange(1, grid_y - 1, 1):
            
            #set Q = 1 2 3 bias to 1 
            # 1: straight, 2: down and right, 3:down and left
            Q=np.random.choice([1, 2, 3], p=(0.34, 0.33, 0.33))

            # if the volume of sediment on the grid is a single layer
            if grid[i, j] == 1:

		#decide if it is going  to move
                QQ = np.random.choice([0, 1], p = (1 - singlelayer_speed, singlelayer_speed))
		
                if QQ == 0:                 
                    grid[i, j] = grid[i, j] # this ia redundant

                elif QQ == 1:
                    
                   # move direction
                   if Q == 1:

                       grid[i, j] = grid[i, j] - 1
                       grid[i+1, j] = grid[i + 1, j] + 1
   
                   elif Q == 2:

                       grid[i, j] = grid[i, j] - 1
                       grid[i+1, j+1] = grid[i+1, j+1] + 1
               
                   elif Q == 3:
                    
                       grid[i, j] = grid[i, j] - 1
                       grid[i+1, j-1] = grid[i+1, j-1] + 1
            # if cell is still populated with more than one layer
            if grid[i, j] > 1:

                #decide if the sediment is going to move
                P = np.random.choice([0, 1], p=(1-multilayer_speed, multilayer_speed))

                if P == 0:
                    grid[i, j]=grid[i, j]

		#move one layer of sediment
                if P == 1:
            	     
                    if Q == 1:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j] = grid[i+1, j] + 1
       
                    elif Q == 2:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j+1] = grid[i+1, j+1] + 1
                   
                    elif Q == 3:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j-1] = grid[i+1, j-1] + 1
         
    # loop over all the cells not on a slope 
    for i in np.arange(grid_x_slope_length-1, grid_x-1, 1):
        for j in np.arange(1, grid_y-1, 1):
            
            # decide if this is going to move or not
            QQQ = np.random.choice((0, 1), p=[1-flatspeed, flatspeed])

            if QQQ == 0:
                grid[i, j] = grid[i, j] # this ia redundant
                
            elif QQQ == 1:
		# move sediment straight if single layer
                if grid[i, j] == 1:
                   grid[i, j] = grid[i, j]-1 
                   grid[i+1, j] = grid[i+1, j]+1
                # if is now a multi layer then choosee a direction to move 
		# and move one layer of sediment to the new position.
                # TODO: now we are on a flat, is the chance of moving straight
                # really higher than any other direction and can it move
                # backwards?
                if grid[i, j] > 1:
                    QQQQ = np.random.choice((1, 2, 3), p=[0.4, 0.3, 0.3])
                    
                    if QQQQ == 1:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j] = grid[i+1, j] + 1
                        
                    if QQQQ == 2:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j-1] = grid[i+1, j-1] + 1

                    if QQQQ == 3:
                        grid[i, j] = grid[i, j] - 1
                        grid[i+1, j+1] = grid[i+1, j+1] + 1
   
    # for every Idel-th tick with 0 offset
    if ticks % Idel == 0:
        
	# loop over all cells where sedment can be deposited
        for i in np.arange(0, del_area, 1):
            for j in np.arange(0, grid_y-1, 1):
                # TODO: I suspect this is a bug and should be grid[i, j] += np.random.choice(..
		# remove existing sediment and replace with a random amount of sediment
                grid[i, j] = np.random.choice(
                        [0, 1, 2, 3, 4, 5, 6, 7], 
                        p=[1-coverage, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7]
                        )
    
    # Remove and multi layer sediments in the inner area
    for i in np.arange(1, grid_x-1, 1):
        for j in np.arange (1, grid_y-1, 1):
            if grid[i, j] < 0:
               grid[i, j] = 0

    # Remove all sediment in the buffer zone at the end of the grid
    for i in np.arange(grid_x-dropzone, grid_x, 1):
        for j in np.arange (0, grid_y, 1):
            grid[i, j] = 0
	
   
    # count cells that are not in the buffer
    # count the quantity of sediment that is not in the buffer 
    for i in np.arange(1, grid_x-dropzone, 1):
        for j in np.arange(1, grid_y-1, 1):
            if grid[i,  j] >= 1:
                cells_with_sediment=cells_with_sediment+1
                sediment_on_grid = sediment_on_grid + grid[i, j]

    # append sediment counts to global array
    Xlist.append(cells_with_sediment)
    XXlist.append(sediment_on_grid)
    
    # count the cells with sediment on the slope 
    # count the quantity of sediment on the slope
    for i in np.arange(1, grid_x_slope_length, 1):
        for j in np.arange(1, grid_y,  1):
            if grid[i, j] > 0:
                slope_cells_with_sediment = slope_cells_with_sediment+1
                sediment_on_slope = sediment_on_slope + grid[i, j]

    # append sediment counts to global array
    Ylist.append(slope_cells_with_sediment)
    YYlist.append(sediment_on_slope)
                
    # count cells with any sediment on the flat
    # count total sediment on the flat
    for i in np.arange(grid_x_slope_length, grid_x, 1):
        for j in np.arange(1, grid_y, 1):
            if grid[i, j] > 0:
                flat_cells_with_sediment = flat_cells_with_sediment+1
                sediment_on_flat = sediment_on_flat + grid[i, j]

    # append sediment counts to global array
    Zlist.append(flat_cells_with_sediment)
    ZZlist.append(sediment_on_flat)
    
    
    print(ticks)
    print('total coverage', cells_with_sediment)
    print('coverage on slope', slope_cells_with_sediment)
    print('Volume on Slope', sediment_on_slope)
    print('coverage on flat', flat_cells_with_sediment)
    print('Volume on flat', sediment_on_flat)
    
    return grid, Xlist, Ylist, Zlist, XXlist, YYlist, ZZlist #redundant
                



# Evolve surface over time, plot and save result per timestep

def run(ticks, grid_x_slope_length, grid_x, Idel, del_area, grid_y, coverage,  singlelayer_speed, multilayer_speed, flatspeed, drop_zone):
    
    for tick in np.arange(1, ticks, 1):

        starttime = time.time()
        cellrules(grid_x_slope_length, grid_x, Idel, del_area, grid_y, coverage, singlelayer_speed, multilayer_speed, flatspeed, drop_zone)
        endtime = time.time()

        flag = 'CAmovie%s' % str(tick)    
        pyplot.figure(figsize=(12, 12))
        pyplot.imshow(grid, cmap='coolwarm', label=flag)
        cbar=pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], orientation='horizontal')
        pyplot.tick_params(axis='y', direction='out')
        pyplot.tick_params(axis='x', direction='out')
 #       plt.savefig("%s.png" % flag)
        #pyplot.clf() # clear fig to prevent ticks plots being stored in memory
#        pyplot.show()
        

        print("tick: {} complete:\n\tItteration took {:0.4f}s".format(tick, endtime - starttime))

# run functions

run(ticks,
        grid_x_slope_length,
        grid_x, ticks_per_delivery,
        delivery_zone,
        grid_y,
        coverage,
        singlelayer_speed,
        multilayer_speed,
        flat_speed,
        drop_zone
    )

pyplot.figure(figsize=(10, 10))
pyplot.plot(Xlist, label='Total coverage')
pyplot.plot(XXlist, label='total Volume')
pyplot.plot(Ylist, label='Slope coverage')
pyplot.plot(YYlist, label='Slope Volume')
pyplot.plot(Zlist, label='Flat coverage')
pyplot.plot(ZZlist, label='Flat Volume')
pyplot.legend(loc='best')

#pyplot.show()
