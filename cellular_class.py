import cellular
import logging
import cell_view
import time
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def run_experiment_MPL_ani(ex, show_plots=True, save_images=True, ticks=50):
    log = logging.getLogger('Experiment')

    fig = cell_view.init_plot(ex.grid)

    def updatefig(n, ex, fig):
        start_time = time.time()
        ex.tick()
        end_time = time.time()
        tick_time = end_time - start_time


        start_time = time.time()
        cell_view.plot_grid(ex.grid, ex.age, show=False, save=True, animated=True, fig=fig)
        end_time = time.time()
        draw_time = end_time - start_time

        log.info("tick: {} complete:\n\tGrid update took {:0.4f}s, drawing: {:0.4f}s".format(ex.age, tick_time, draw_time))

    # you need to assign the result to a variable otherwise it fails..
    ani = animation.FuncAnimation(fig, updatefig, frames=ticks, repeat=False, interval=1, blit=False, fargs=(ex, fig))
    pyplot.show()



def run_experiment_MPL(ex, show_plots=True, save_images=True, ticks=50):
    log = logging.getLogger('Experiment')

    # decide if we are going to show plots online and if we are going save the images for creating the video at the end.
    show_live_plots = show_plots
    save_images = save_images

    # init plotting
    fig = cell_view.init_plot(ex.grid)

    # generate a plot of the initial conditions.
    cell_view.plot_grid(ex.grid, tick=0, show=show_live_plots, save=save_images, fig=fig)

    while ex.age < ticks:
        # start timer
        start_time = time.time()
        # do the tick and update the grid
        ex.tick()
        # stop timer and report how long the tick took in realtime
        end_time = time.time()
        log.info("tick: {} complete:\n\tIterations took {:0.4f}s".format(ex.age, end_time - start_time))

        # plot the new data
        cell_view.plot_grid(ex.grid, tick=ex.age, show=show_live_plots, save=save_images, fig=fig)
    cell_view.generate_video('video', 'png', cell_view.get_ffmpeg_path(), (1200, 1200), fps=2)


ex1 = cellular.Experiment(225, 200,
    coverage=0.01,
    slope_length=200,
    ticks_per_delivery=5,
    delivery_zone=1,
    singlelayer_speed=0.25,
    multilayer_speed=0.6,
    flat_speed=0.05,
    drop_zone=1
    )


run_experiment_MPL_ani(ex1,ticks=300)

# cell_view.generate_video('video', 'png', ffmpeg_exe, (1200, 1200), fps=1)
