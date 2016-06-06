import cellular
import logging
import platform
import cell_view
import time

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

if 'windows' in platform.platform().lower():
    ffmpeg_exe = 'c:\\Program Files (x86)\\ffmpeg-20160531-git-a1953d4-win64-static\\bin\\ffmpeg.exe'
else:
    ffmpeg_exe = 'ffmpeg'





def run_experiment_MPL(ex, show_plots=True, save_images=True, ticks=50):
    log = logging.getLogger('Experiment')

    # decide if we are going to show plots online and if we are going save the images for creating the video at the end.
    show_live_plots = show_plots
    save_images = save_images

    # init plotting
    fig = cell_view.init_plot()

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



ex1 = cellular.Experiment(640, 480,
    coverage=0.15,
    slope_length=450,
    ticks_per_delivery=5,
    delivery_zone=2,
    singlelayer_speed=0.3,
    multilayer_speed=0.7,
    flat_speed=0.2,
    drop_zone=1
    )


run_experiment_MPL(ex1)



# grid = cellular.init_grid(640, 480, coverage=0.15)
# cellular.run(grid,
#     ticks=5,
#     slope_length=450,
#     ticks_per_delivery=5,
#     delivery_zone=2,
#     coverage=0.15,
#     singlelayer_speed=0.3,
#     multilayer_speed=0.7,
#     flat_speed=0.2,
#     drop_zone=1
#     )

#cellular.generate_video('video', 'png', ffmpeg_exe, (1200, 1200), fps=1)