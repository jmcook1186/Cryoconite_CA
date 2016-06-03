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
import platform
import os
import subprocess as sp


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
            # this was a bug, changed to +=
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
    



def init_plot():
    pyplot.ioff()
    fig = pyplot.figure(figsize=(12, 12))
    return fig

def plot_grid(grid, tick=0, show=False, save=False, fig=None):        
    if fig is not None:
        pass
        #fig.canvas.clear()
    else:
        fig = pyplot.figure(figsize=(12, 12))
        
    pyplot.title = ('Sediment density at time: {}'.format(tick))

    flag = 'CAmovie%s' % str(tick)    
    pyplot.imshow(grid, cmap='coolwarm', label=flag, vmin=0, vmax=50)
    fig.canvas.draw()
    cbar=pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], orientation='horizontal')
    pyplot.tick_params(axis='y', direction='out')
    pyplot.tick_params(axis='x', direction='out')
    if show:
        pyplot.ion()
        pyplot.show()

    if save:
        fig.savefig(os.path.join('tmp_image', "%s.png" % flag))
    pyplot.clf() # clear fig to prevent ticks plots being stored in memory
        


def update_grid(grid, slope_length, slope_singlelayer_speed, slope_multilayer_speed, flat_speed, ticks_per_delivery):
    def move(grid, i, j, direction):
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
        # as planned
	#
	# TODO: check if bug that you are not using a buffer.
	# as material moves down the slope, it will be picked up in the next itteration of the grid_x loop.
	# so it is perfectly possible for sediment to be deposited at the top of the slope and traerse the whole slope in one itteration.
        # this is a bug. need to use temp array
	
        for j in np.arange(1, grid.shape[1] - 1, 1):       
            # if the volume of sediment on the grid is a single layer
            if grid[i, j] == 1 and single_chance_of_moving[i,j] > 0:
                
            #     if single_chance_of_moving[i,j] > 0:
                    #Q=np.random.choice([1, 2, 3], p=(0.34, 0.33, 0.33))
                    move(new_grid, i, j, single_chance_of_moving[i,j])        

            # if cell is still populated with more than one layer
            elif grid[i, j] > 1 and multi_chance_of_moving[i,j] > 0:

                #decide if the sediment is going to move
                #P = np.random.choice([0, 1], p=(1-slope_multilayer_speed, slope_multilayer_speed))

		#move one layer of sediment
            #    if multi_chance_of_moving[i,j] > 0:
                    #Q=np.random.choice([1, 2, 3], p=(0.34, 0.33, 0.33))
                    move(new_grid, i, j, multi_chance_of_moving[i,j])	     
         
    # loop over all the cells not on a slope 
    for i in np.arange(slope_length-1, grid.shape[0]-1, 1):
        for j in np.arange(1, grid.shape[1]-1, 1):
                     
            if flat_chance_of_moving[i,j] > 0:
            # decide if this is going to move or not
                #QQQ = np.random.choice((0, 1), p=[1-flat_speed, flat_speed])
                #if QQQ == 1:
                    # move sediment straight if single layer
                if grid[i, j] == 1:
                    move(new_grid, i, j, 1)
                else:        
                    move(new_grid, i, j, flat_chance_of_moving[i,j])


                    # if is now a multi layer then choose a direction to move 
                    # and move one layer of sediment to the new position.
                    # TODO: now we are on a flat, is the chance of moving straight
                    # really higher than any other direction and can it move
                    # backwards?
#                    if grid[i, j] > 1:
#                        QQQQ = np.random.choice((1, 2, 3), p=[0.4, 0.3, 0.3])
#                        move(QQQQ) 
    return new_grid


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

def clense_tmp_images():
    # delete any files saved from previous runs
    for ext in ["bmp", "png"]:
        path = os.path.join('tmp_images', '*.{}'.format(ext))
        for f in glob.glob(path):
            os.unlink(f) 

def generate_video(video_filename, image_format,  ffmpeg_exe, size, video_length=None, fps=5):
    size_str = '{}x{}'.format(1200, 891)
    command = [ffmpeg_exe,]
    if video_length is not None:
        command.extend(['-t', '{}'.format(video_length)])
    command.extend([
        '-y',  # (optional) overwrite output file if it exists
        '-r', '{}'.format(fps),  # frames per second
        '-i', os.path.join('tmp_image', 'CAmovie%d.{}'.format(image_format)),
        '-s', size_str,
        '-an',  # Tells FFMPEG not to expect any audio
        '-c:v', 'qtrle',
        '-tune', 'animation',
        '-q', '0',
        '-s', size_str,  # size of one frame
        '{}.mov'.format(video_filename)
        ]
    )
    #print (' '.join(command))
    sp.call(command)

# Evolve surface over time, plot and save result per timestep
def run(grid, ticks, slope_length, ticks_per_delivery, delivery_zone, coverage,  singlelayer_speed, multilayer_speed, flat_speed, drop_zone):




    tick = 0
    fig = init_plot()
    show_live_plots = True
    save_images = False
    plot_grid(grid, tick=0, show=show_live_plots, save=save_images, fig=fig)
    for i in range(ticks):
        starttime = time.time()
        grid = update_grid(grid, slope_length, singlelayer_speed, multilayer_speed,  flat_speed, ticks_per_delivery)
        if tick % ticks_per_delivery == 0:
            add_sediment(grid, (0, delivery_zone)) 
        remove_sediment(grid, (grid.shape[0]-drop_zone, grid.shape[0]))  
        grid_stats(slope_length, grid[:-drop_zone,])
        endtime = time.time()
        print("tick: {} complete:\n\tItteration took {:0.4f}s".format(tick, endtime - starttime))
        tick += 1
        plot_grid(grid, tick=tick, show=show_live_plots, save=save_images, fig=fig)
        #input() 

    

# run functions
if __name__ == "__main__":
    if 'windows' in platform.platform().lower():
            ffmpeg_exe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
    else:
            ffmpeg_exe = 'ffmpeg'

    grid = init_grid(175, 150, coverage = 0.15)
    run(    grid,
            ticks=20,
            slope_length=150,
            ticks_per_delivery = 30,
            delivery_zone = 10,
            coverage = 0.15,
            singlelayer_speed=0.3,
            multilayer_speed=0.7,
            flat_speed=0.2,
            drop_zone=6
       )

    generate_video('video','png', 'ffmpeg', grid.shape, fps=1)
