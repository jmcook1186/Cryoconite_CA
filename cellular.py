#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tuesday April 26 07:07:54 2016

@author: Joseph

"""

import numpy as np
np.random.seed(0)

import time
import logging
from collections import namedtuple





# define a named tuple for the experimental parameters
config_tuple = namedtuple('experiment_config', ' coverage  slope_length '
                                               ' ticks_per_delivery delivery_zone'
                                               ' singlelayer_speed multilayer_speed '
                                               ' flat_speed drop_zone'
                                               ' slope_direction_probability flat_direction_probability'
                                               ' max_sediment_per_deposit'
                          )

class Experiment(object):
    def __init__(self, x, y,
                 coverage,
                 slope_length,
                 ticks_per_delivery, delivery_zone,
                 singlelayer_speed, multilayer_speed,
                flat_speed, drop_zone):

        self.grid = init_grid(x, y, coverage)
        self.age = 0
        self.config = config_tuple(
            coverage,
            slope_length,
            ticks_per_delivery,
            delivery_zone,
            singlelayer_speed,
            multilayer_speed,
            flat_speed,
            drop_zone,
            np.array((0.34, 0.33, 0.33)),
            np.array((0.4, 0.3, 0.3)),
            max_sediment_per_deposit=7
        )

        # self.coverage = coverage
        # self.slope_length = slope_length
        # self.ticks_per_delivery = ticks_per_delivery
        # self.delivery_zone = delivery_zone
        # self.singlelayer_speed = singlelayer_speed
        # self.multilayer_speed = multilayer_speed
        # self.flat_speed = flat_speed
        # self.drop_zone = drop_zone

    def remove_sediment(self):
        remove_sediment(self.grid, (self.grid.shape[0] - self.config.drop_zone, self.grid.shape[0]))

    def add_sediment(self):
        deposit_sediment(self.grid,
                         self.config.delivery_zone,
                         self.config.max_sediment_per_deposit,
                         coverage=self.config.coverage
                         )

    def tick(self):
        if self.age % self.config.ticks_per_delivery == 0:
            self.add_sediment()
        self.remove_sediment()

        self.grid = update_grid(self.grid, self.config.slope_length, self.config.singlelayer_speed,
                    self.config.multilayer_speed, self.config.flat_speed)

        grid_stats(self.config.slope_length, self.grid[:-self.config.drop_zone, ])
        self.age += 1
        return self.grid


def init_grid(x, y, coverage, sediment=7, probability=None):
    grid = np.zeros((x, y))
    deposit_sediment(grid, x, sediment, probability, coverage)
    return grid

def deposit_sediment(grid, deposit_zone, sediment=7, probability=None, coverage=0.15):
    log = logging.getLogger('sediment.add')

    try:
        sediment = int(sediment)
        sediment_choice = [0]
        sediment_choice.extend(range(1, sediment + 1))
    except:
        sediment_choice = sediment

    if probability is None:
        probability = [1 - coverage]
        probability.extend((coverage / (len(sediment_choice) - 1),) * (len(sediment_choice) - 1))


    #log.info('adding sediment in the area {}x{} with coverage {:0.3f} with amounts: {} '.format(deposit_zone, grid.shape[1], coverage, ', '.join([str(i) for i in sediment_choice])))

    deposit = np.random.choice(
        sediment_choice,
        (deposit_zone, grid.shape[1]),
        p=probability
    )

    grid[:deposit_zone, :] += deposit

    io = sediment_summary(deposit)
    log.info('{1} sediment added over {0} cells in the area {2}x{3}'.format(io[0], io[1], deposit_zone, grid.shape[1]))
    return io


def remove_sediment(grid, dropzone):
    log = logging.getLogger('sediment.remove')
    # Remove all check to ensure that no negative values.
    for i in np.arange(1, grid.shape[0] - 1, 1):
        for j in np.arange(1, grid.shape[1] - 1, 1):
            if grid[i, j] < 0:
                logging.getLogger().warn('found illegal value({}) at {},{}'.format(grid[i, j], i, j))
                grid[i, j] = 0

    io = sediment_summary(grid[dropzone[0]:dropzone[1], :])

    # Remove all sediment in the buffer zone at the end of the grid
    grid[dropzone[0]:dropzone[1], :] = 0

    log.info('{1} sediment removed from {0} cells.'.format(*io))
    return io

    # for i in np.arange(dropzone[0], dropzone[1], 1):
    #     for j in np.arange(0, grid.shape[1], 1):
    #         grid[i, j] = 0


def sediment_summary(grid):
    return np.count_nonzero(grid), np.sum(grid)

def grid_stats(slope_length, grid):


    cells_with_sediment, sediment_on_grid = sediment_summary(grid[1:, 1:-1])
    slope_cells_with_sediment, sediment_on_slope = sediment_summary(grid[1:slope_length, 1:-1])
    flat_cells_with_sediment, sediment_on_flat = sediment_summary(grid[slope_length:, 1:-1])

    log = logging.getLogger('summary')
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
    pyplot.imshow(grid, cmap='coolwarm', label=flag, vmin=0, vmax=20)
    fig.canvas.draw()
    cbar = pyplot.colorbar(ticks=np.arange(0,20,1), orientation='horizontal')
    pyplot.tick_params(axis='y', direction='out')
    pyplot.tick_params(axis='x', direction='out')
    if show:
        pyplot.ion()
        pyplot.show()

    if save:
        fig.savefig(os.path.join('tmp_image', "%s.png" % flag))
    pyplot.clf()  # clear fig to prevent ticks plots being stored in memory


def update_grid(grid, slope_length, slope_singlelayer_speed, slope_multilayer_speed, flat_speed):
    log = logging.getLogger('tick')
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
    p = [1 - flat_speed]
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



    #log.info('{} sediment from {} cells moved on slope'.format())
    #log.info('{} sediment from {} cells moved from slope to flat'.format())
    #log.info('{} sediment from {} cells moved on flat'.format())

    return new_grid




# Evolve surface over time, plot and save result per timestep
def evolve(grid, add_sediment, delete_sediment, slope_length, singlelayer_speed, multilayer_speed, flat_speed, delivery_zone, coverage, drop_zone):
    '''
    apply rules to a surface and return the updated surface.

    :param grid:
    :param add_sediment: should we deposit sediment on the surface on this tick
    :param delete_sediment: should we remove sediment from the surface on this tick
    :param slope_length:
    :param singlelayer_speed:
    :param multilayer_speed:
    :param flat_speed:
    :param delivery_zone:
    :param coverage:
    :param drop_zone:
    :return:
    '''

    grid = update_grid(grid, slope_length, singlelayer_speed, multilayer_speed, flat_speed)
    if add_sediment:
        deposit_sediment(grid, delivery_zone, coverage=coverage)
    if delete_sediment:
        remove_sediment(grid, (grid.shape[0] - drop_zone, grid.shape[0]))

    grid_stats(slope_length, grid[:-drop_zone, ])

    return grid


def run(grid, ticks, slope_length, ticks_per_delivery, delivery_zone, coverage, singlelayer_speed, multilayer_speed,
        flat_speed, drop_zone):
    '''


    :param grid:
    :param ticks:
    :param slope_length:
    :param ticks_per_delivery:
    :param delivery_zone:
    :param coverage:
    :param singlelayer_speed:
    :param multilayer_speed:
    :param flat_speed:
    :param drop_zone:
    :return:
    '''
    log = logging.getLogger()


    #decide if we are going to show plots online and if we are going save the images for creating the video at the end.
    show_live_plots = True
    save_images = True

    # init plotting
    fig = cell_view.init_plot()

    # generate a plot of the initial conditions.
    cell_view.plot_grid(grid, tick=0, show=show_live_plots, save=save_images, fig=fig)


    for tick in range(ticks):
        #start timer
        start_time = time.time()

        # decide if we want to deposit more on the surface.
        if tick % ticks_per_delivery == 0:
            add_sediment = True
        else:
            add_sediment = False

        # do the tick and update the grid
        grid = evolve(
            grid,
            add_sediment, True,
            slope_length,
            singlelayer_speed, multilayer_speed, flat_speed, delivery_zone, coverage, drop_zone
        )

        #stop timer and report how long the tick took in realtime
        end_time = time.time()
        log.info("tick: {} complete:\n\tIterations took {:0.4f}s".format(tick, end_time - start_time))

        # plot the new data
        cell_view.plot_grid(grid, tick=tick, show=show_live_plots, save=save_images, fig=fig)


# run functions
if __name__ == "__main__":
    import cell_view

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    if 'windows' in platform.platform().lower():
        ffmpeg_exe = 'c:\\Program Files (x86)\\ffmpeg-20160531-git-a1953d4-win64-static\\bin\\ffmpeg.exe'
    else:
        ffmpeg_exe = 'ffmpeg'

    grid = init_grid(640, 480, coverage=0.15)


    cell_view.clense_tmp_images()

    run(grid,
        ticks=5,
        slope_length=450,
        ticks_per_delivery=5,
        delivery_zone=2,
        coverage=0.15,
        singlelayer_speed=0.3,
        multilayer_speed=0.7,
        flat_speed=0.2,
        drop_zone=1
        )
    cell_view.generate_video('video', 'png', ffmpeg_exe, (1200, 1200), fps=1)
