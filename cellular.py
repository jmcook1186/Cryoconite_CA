#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tuesday April 26 07:07:54 2016

@author: Joseph

"""

import numpy as np
np.random.seed(0)
import matplotlib.pyplot as pyplot
import time
import copy



def init_grid(x, y, coverage, sediment=7, probability=None):
    try:
        sediment = int(sediment)
        sediment_choice = [0]
        sediment_choice.extend(range(1, sediment+1))
    except:
        sediment = sediment_choice

    if probability is None:
        probability = [1-coverage]
        probability.extend((coverage/(len(sediment_choice)-1),)*(len(sediment_choice)-1))

    return np.random.choice(
            sediment_choice,
            (x, y), 
            p=probability
    )


def remove_sediment(grid, dropzone):
    # Remove all check to ensure that no negative values.
    for i in np.arange(1, grid.shape[0]-1, 1):
        for j in np.arange (1, grid.shape[1]-1, 1):
            if grid[i, j] < 0:
               grid[i, j] = 0

    # Remove all sediment in the buffer zone at the end of the grid
    for i in np.arange(dropzone[0], dropzone[1], 1):
        for j in np.arange (0, grid.shape[1], 1):
            grid[i, j] = 0
	



def add_sediment(grid, deposit_zone):
    print('WARNING: FIXME: HARDCODED VALUE IN ADD_SEDIMENT FXN')
    coverage = 0.85
    # for every Idel-th tick with 0 offset
    # loop over all cells where sedment can be deposited
    for i in np.arange(deposit_zone[0], deposit_zone[1]):
        for j in np.arange(0, grid.shape[1]-1, 1):
            # TODO: I suspect this is a bug and should be grid[i, j] += np.random.choice(..
            # remove existing sediment and replace with a random amount of sediment
            grid[i, j] += np.random.choice(
                    [0, 1, 2, 3, 4, 5, 6, 7], 
                    p=[1-coverage, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7, coverage/7]
                    )




def grid_stats(slope_length, grid,  print_to_stdout=True):

    # Initialize variables for stats
    cells_with_sediment = 0
    sediment_on_grid = 0

    slope_cells_with_sediment = 0
    sediment_on_slope = 0

    flat_cells_with_sediment = 0
    sediment_on_flat = 0
    def get_summary(grid):
        cells_with_sediment = np.count_nonzero(grid)
        sediment_on_grid = np.sum(grid)
        return (cells_with_sediment, sediment_on_grid)
    cells_with_sediment, sediment_on_grid = get_summary(grid[1:, 1:-1])
    slope_cells_with_sediment, sediment_on_slope = get_summary(grid[1:slope_length, 1:])
    flat_cells_with_sediment, sediment_on_flat = get_summary(grid[slope_length:, 1:])

    # count cells that are not in the buffer
    # count the quantity of sediment that is not in the buffer 

    #for i in np.arange(1, grid.shape[0], 1):
    #    for j in np.arange(1, grid.shape[1]-1, 1):
    #        if grid[i,  j] >= 1:
    #            cells_with_sediment=cells_with_sediment+1
    #            sediment_on_grid = sediment_on_grid + grid[i, j]
    

    
    
    # count the cells with sediment on the slope 
    # count the quantity of sediment on the slope
    #for i in np.arange(1, slope_length, 1):
    #    for j in np.arange(1, grid.shape[1],  1):
    #        if grid[i, j] > 0:
    #            slope_cells_with_sediment = slope_cells_with_sediment+1
    #            sediment_on_slope = sediment_on_slope + grid[i, j]

                
    # count cells with any sediment on the flat
    # count total sediment on the flat
    #for i in np.arange(slope_length, grid.shape[0], 1):
    #    for j in np.arange(1, grid.shape[1], 1):
    #        if grid[i, j] > 0:
    #            flat_cells_with_sediment = flat_cells_with_sediment+1
    #            sediment_on_flat = sediment_on_flat + grid[i, j]

    if print_to_stdout:
        print('total coverage', cells_with_sediment)
        print('coverage on slope', slope_cells_with_sediment)
        print('Volume on Slope', sediment_on_slope)
        print('coverage on flat', flat_cells_with_sediment)
        print('Volume on flat', sediment_on_flat)

# append sediment counts to global array
    return ( 
        cells_with_sediment, 
        sediment_on_grid,
        slope_cells_with_sediment,
        sediment_on_slope,
        flat_cells_with_sediment,
        sediment_on_flat
    )
    




def plot_grid(grid, tick=0, show=False, save=False):        
    pyplot.figure(figsize=(12, 12))
    pyplot.title = ('Sediment density at time: {}'.format(tick))

    flag = 'CAmovie%s' % str(tick)    
    pyplot.imshow(grid, cmap='coolwarm', label=flag)
    cbar=pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], orientation='horizontal')
    pyplot.tick_params(axis='y', direction='out')
    pyplot.tick_params(axis='x', direction='out')
    if show:
        pyplot.show()

    if save:
        plt.savefig("%s.png" % flag)
        pyplot.clf() # clear fig to prevent ticks plots being stored in memory
        


def update_grid(grid, slope_length, slope_singlelayer_speed, slope_multilayer_speed, flat_speed, ticks_per_delivery):
    def move(direction):
        # decrement one unit of sediment from current cell 
        grid[i, j] -= 1

        # increment cell in the right direction
        if direction == 1: # straight
            grid[i+1, j] += 1
   
        elif direction == 2: # diagonal
            grid[i+1, j+1] += 1
               
        elif direction == 3: # diagonal
            grid[i+1, j-1] += 1

    new_grid = np.copy(grid)
    
    slope_direction_probability = np.array((0.34, 0.33, 0.33))
    single_chance_of_moving = np.random.choice([0, 1, 2, 3], 
            grid.shape, 
            p = [1 - slope_singlelayer_speed ].extend(slope_direction_probability * slope_singlelayer_speed)
        )
    multi_chance_of_moving = np.random.choice([0, 1, 2, 3], 
            grid.shape, 
            p = [1 - slope_multilayer_speed ].extend(slope_direction_probability * slope_multilayer_speed)
        )
    flat_direction_probability = np.array((0.4, 0.3, 0.3))
    flat_chance_of_moving = np.random.choice([0, 1, 2, 3], 
            grid.shape, 
            p = [1 - flat_speed ].extend(flat_direction_probability * flat_speed)
        )

    # for each cell on the slope
    for i in np.arange(0, slope_length, 1):
        # TODO: check if this is a bug, 
	# the loop is skips the left-most and rightmost columns, so material can 
	# fall off the side of the grid, but it is not able to re-enter
	#
	# TODO: check if bug that you are not using a buffer.
	# as material moves down the slope, it will be picked up in the next itteration of the grid_x loop.
	# so it is perfectly possible for sediment to be deposited at the top of the slope and traerse the whole slope in one itteration.
	
        for j in np.arange(1, grid.shape[1] - 1, 1):       
            # if the volume of sediment on the grid is a single layer
            if grid[i, j] == 1 and single_chance_of_moving[i,j] > 0:
                
                #if QQ == 0:                 
                #    new_grid[i, j] = grid[i, j] 

            #     if single_chance_of_moving[i,j] > 0:
                    #Q=np.random.choice([1, 2, 3], p=(0.34, 0.33, 0.33))
                    move(single_chance_of_moving[i,j])        

            # if cell is still populated with more than one layer
            elif grid[i, j] > 1 and multi_chance_of_moving[i,j] > 0:

                #decide if the sediment is going to move
                #P = np.random.choice([0, 1], p=(1-slope_multilayer_speed, slope_multilayer_speed))

		#move one layer of sediment
            #    if multi_chance_of_moving[i,j] > 0:
                    #Q=np.random.choice([1, 2, 3], p=(0.34, 0.33, 0.33))
                    move(multi_chance_of_moving[i,j])	     
         
    # loop over all the cells not on a slope 
    for i in np.arange(slope_length-1, grid.shape[0]-1, 1):
        for j in np.arange(1, grid.shape[1]-1, 1):
                     
            if flat_chance_of_moving[i,j] > 0:
            # decide if this is going to move or not
                #QQQ = np.random.choice((0, 1), p=[1-flat_speed, flat_speed])
                #if QQQ == 1:
                    # move sediment straight if single layer
                if grid[i, j] == 1:
                    move(1)
                else:        
                    move(flat_chance_of_moving[i,j])


                    # if is now a multi layer then choose a direction to move 
                    # and move one layer of sediment to the new position.
                    # TODO: now we are on a flat, is the chance of moving straight
                    # really higher than any other direction and can it move
                    # backwards?
#                    if grid[i, j] > 1:
#                        QQQQ = np.random.choice((1, 2, 3), p=[0.4, 0.3, 0.3])
#                        move(QQQQ) 
    return grid


def report():
    pyplot.figure(figsize=(10, 10))
    pyplot.plot(Xlist, label='Total coverage')
    pyplot.plot(XXlist, label='total Volume')
    pyplot.plot(Ylist, label='Slope coverage')
    pyplot.plot(YYlist, label='Slope Volume')
    pyplot.plot(Zlist, label='Flat coverage')
    pyplot.plot(ZZlist, label='Flat Volume')
    pyplot.legend(loc='best')
    pyplot.show()

# Evolve surface over time, plot and save result per timestep
def run(grid, ticks, slope_length, ticks_per_delivery, delivery_zone, coverage,  singlelayer_speed, multilayer_speed, flat_speed, drop_zone):
     
    #plot_grid(grid, tick=0, save=False)
    for tick in np.arange(1, ticks, 1):
        starttime = time.time()
        next_grid =  update_grid(grid, slope_length, singlelayer_speed, multilayer_speed,  flat_speed, ticks_per_delivery)
        if tick % ticks_per_delivery == 0:
            add_sediment(grid, (0, delivery_zone)) 
        remove_sediment(grid, (grid.shape[0]-drop_zone, grid.shape[0]))  
        grid_stats(slope_length, grid[:-drop_zone,])
        endtime = time.time()

        plot_grid(grid, tick=tick, save=False)
        print("tick: {} complete:\n\tItteration took {:0.4f}s".format(tick, endtime - starttime))

# run functions
if __name__ == "__main__":
    grid = init_grid(175, 150, coverage = 0.15)

    # define automaton rules
    run(    grid,
            ticks=5,
            slope_length=150,
            ticks_per_delivery = 3,
            delivery_zone = 10,
            coverage = 0.15,
            singlelayer_speed=0.3,
            multilayer_speed=0.7,
            flat_speed=0.2,
            drop_zone=6
        )
    pyplot.show()
#    report()

