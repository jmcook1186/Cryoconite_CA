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
import platform
import os
import subprocess as sp
import logging
import glob
import sys


def init_grid(x, y, coverage, sediment=7, probability=None):
    print(coverage)
    grid = np.zeros((x, y))
    deposit_sediment(grid, x, sediment, probability, coverage)
    return grid

def deposit_sediment(grid, deposit_zone, sediment=7, probability=None, coverage=0.15):
    log = logging.getLogger()

    try:
        sediment = int(sediment)
        sediment_choice = [0]
        sediment_choice.extend(range(1, sediment + 1))
    except:
        sediment_choice = sediment

    if probability is None:
        probability = [1 - coverage]
        probability.extend((coverage / (len(sediment_choice) - 1),) * (len(sediment_choice) - 1))


    log.info('adding sediment in the area {}x{} with coverage {:0.3f} with amounts: {} '.format(deposit_zone, grid.shape[1], coverage, ', '.join([str(i) for i in sediment_choice])))
    #print(((deposit_zone, grid.shape[1], coverage, ', '.join([str(i) for i in sediment_choice]))))
    #print('adding sediment in the area {}x{} with coverage {:0.3f} with amounts: {} '.format(deposit_zone, grid.shape[1], coverage, ', '.join([str(i) for i in sediment_choice])))

    deposit = np.random.choice(
        sediment_choice,
        (deposit_zone, grid.shape[1]),
        p=probability
    )

    grid[:deposit_zone, :] += deposit


def remove_sediment(grid, dropzone):
    # Remove all check to ensure that no negative values.
    for i in np.arange(1, grid.shape[0] - 1, 1):
        for j in np.arange(1, grid.shape[1] - 1, 1):
            if grid[i, j] < 0:
                logging.getLogger().warn('found illegal value({}) at {},{}'.format(grid[i, j], i, j))
                grid[i, j] = 0

    # Remove all sediment in the buffer zone at the end of the grid

    grid[dropzone[0]:dropzone[1], :] = 0

    # for i in np.arange(dropzone[0], dropzone[1], 1):
    #     for j in np.arange(0, grid.shape[1], 1):
    #         grid[i, j] = 0





def grid_stats(slope_length, grid):
    def get_summary(grid):
        return np.count_nonzero(grid), np.sum(grid)

    cells_with_sediment, sediment_on_grid = get_summary(grid[1:, 1:-1])
    slope_cells_with_sediment, sediment_on_slope = get_summary(grid[1:slope_length, 1:])
    flat_cells_with_sediment, sediment_on_flat = get_summary(grid[slope_length:, 1:])

    log = logging.getLogger('')
    log.info('total coverage: {}'.format(cells_with_sediment))
    log.info('coverage on slope: {}'.format(slope_cells_with_sediment))
    log.info('Volume on Slope: {}'.format(sediment_on_slope))
    log.info('coverage on flat: {}'.format(flat_cells_with_sediment))
    log.info('Volume on flat: {}'.format(sediment_on_flat))

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
        # fig.canvas.clear()
    else:
        fig = pyplot.figure(figsize=(12, 12))

    pyplot.title = ('Sediment density at time: {}'.format(tick))

    flag = 'CAmovie%s' % str(tick)
    pyplot.imshow(grid, cmap='coolwarm', label=flag, vmin=0, vmax=50)
    fig.canvas.draw()
    cbar = pyplot.colorbar(ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], orientation='horizontal')
    pyplot.tick_params(axis='y', direction='out')
    pyplot.tick_params(axis='x', direction='out')
    if show:
        pyplot.ion()
        pyplot.show()

    if save:
        fig.savefig(os.path.join('tmp_image', "%s.png" % flag))
    pyplot.clf()  # clear fig to prevent ticks plots being stored in memory


def update_grid(grid, slope_length, slope_singlelayer_speed, slope_multilayer_speed, flat_speed):
    def move(grid, i, j, direction):
        # decrement one unit of sediment from current cell
        grid[i, j] -= 1

        # increment cell in the right direction
        if direction == 1:  # straight
            grid[i + 1, j] += 1

        elif direction == 2:  # diagonal
            grid[i + 1, j + 1] += 1

        elif direction == 3:  # diagonal
            grid[i + 1, j - 1] += 1

    new_grid = np.copy(grid)

    slope_direction_probability = np.array((0.34, 0.33, 0.33))
    p = [1 - slope_singlelayer_speed]
    p.extend(slope_direction_probability * slope_singlelayer_speed)
    single_chance_of_moving = np.random.choice([0, 1, 2, 3],
                                               grid.shape,
                                               p=p
                                               )
    p = [1 - slope_multilayer_speed]
    p.extend(slope_direction_probability * slope_multilayer_speed)
    multi_chance_of_moving = np.random.choice([0, 1, 2, 3],
                                              grid.shape,
                                              p=p
                                              )


    flat_direction_probability = np.array((0.4, 0.3, 0.3))
    p =  [1 - flat_speed]
    p.extend(flat_direction_probability * flat_speed)
    flat_chance_of_moving = np.random.choice([0, 1, 2, 3],
                                             grid.shape,
                                             p=p
                                             )

    # for each cell on the slope
    for i in np.arange(0, slope_length, 1):
        # TODO: check if this is a bug,
        # the loop is skips the left-most and rightmost columns, so material can
        # fall off the side of the grid, but it is not able to re-enter
        # as planned

        for j in np.arange(1, grid.shape[1] - 1):
            # if the volume of sediment on the grid is a single layer
            if grid[i, j] == 1 and single_chance_of_moving[i, j] > 0:

                #     if single_chance_of_moving[i,j] > 0:
                move(new_grid, i, j, single_chance_of_moving[i, j])

                # if cell is still populated with more than one layer
            elif grid[i, j] > 1 and multi_chance_of_moving[i, j] > 0:
                move(new_grid, i, j, multi_chance_of_moving[i, j])

                # loop over all the cells not on a slope
    for i in np.arange(slope_length, grid.shape[0] - 1, 1):
        for j in np.arange(1, grid.shape[1] - 1, 1):

            if flat_chance_of_moving[i, j] > 0:
                # move sediment straight if single layer
                if grid[i, j] == 1:
                    move(new_grid, i, j, 1)
                elif grid[i, j] > 1:
                    move(new_grid, i, j, flat_chance_of_moving[i, j])

    return new_grid


# def report():
#     pyplot.figure(figsize=(10, 10))
#     pyplot.plot(Xlist, label='Total coverage')
#     pyplot.plot(XXlist, label='total Volume')
#     pyplot.plot(Ylist, label='Slope coverage')
#     pyplot.plot(YYlist, label='Slope Volume')
#     pyplot.plot(Zlist, label='Flat coverage')
#     pyplot.plot(ZZlist, label='Flat Volume')
#     pyplot.legend(loc='best')
#     pyplot.show()

def clense_tmp_images():
    # delete any files saved from previous runs
    log = logging.getLogger()
    for ext in ["bmp", "png"]:
        path = os.path.join('tmp_images', '*.{}'.format(ext))
        files_for_deletion = glob.glob(path)
        if len(files_for_deletion) > 0:
            log.warn('deleted {} images from previous run.'.format(len(files_for_deletion)))
            for f in files_for_deletion:
                os.unlink(f)


def generate_video(video_filename, image_format, ffmpeg_exe, size, video_length=None, fps=5):
    size_str = '{}x{}'.format(1200, 891)
    command = [ffmpeg_exe, ]
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
    # print (' '.join(command))
    sp.call(command)


# Evolve surface over time, plot and save result per timestep
def evolve(grid, tick, slope_length, singlelayer_speed, multilayer_speed, flat_speed, ticks_per_delivery, delivery_zone, coverage, drop_zone):
    #logging.getLogger().info('Tick: {}'.format(tick))
    grid = update_grid(grid, slope_length, singlelayer_speed, multilayer_speed, flat_speed)
    if tick % ticks_per_delivery == 0:
        deposit_sediment(grid, delivery_zone, coverage=coverage)
    remove_sediment(grid, (grid.shape[0] - drop_zone, grid.shape[0]))
    grid_stats(slope_length, grid[:-drop_zone, ])
    return grid


def run(grid, ticks, slope_length, ticks_per_delivery, delivery_zone, coverage, singlelayer_speed, multilayer_speed,
        flat_speed, drop_zone):
    log = logging.getLogger()
    tick = 0
    fig = init_plot()
    show_live_plots = True
    save_images = True
    plot_grid(grid, tick=0, show=show_live_plots, save=save_images, fig=fig)
    for i in range(ticks):
        start_time = time.time()
        grid = evolve(
            grid, tick, slope_length, singlelayer_speed, multilayer_speed, flat_speed, ticks_per_delivery,
            delivery_zone, coverage, drop_zone
        )
        end_time = time.time()
        log.info("tick: {} complete:\n\tIterations took {:0.4f}s".format(tick, end_time - start_time))
        tick += 1
        plot_grid(grid, tick=tick, show=show_live_plots, save=save_images, fig=fig)


# run functions
if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    if 'windows' in platform.platform().lower():
        ffmpeg_exe = 'C:\\Users\\admin\\Desktop\\ffmpeg-20150921-git-74e4948-win64-static\\bin\\ffmpeg.exe'
    else:
        ffmpeg_exe = 'ffmpeg'

    grid = init_grid(640, 480, coverage=0.15)


    clense_tmp_images()

    run(grid,
        ticks=300,
        slope_length=450,
        ticks_per_delivery=5,
        delivery_zone=2,
        coverage=0.15,
        singlelayer_speed=0.3,
        multilayer_speed=0.7,
        flat_speed=0.2,
        drop_zone=1
        )

    generate_video('video', 'png', 'ffmpeg', grid.shape, fps=1)
