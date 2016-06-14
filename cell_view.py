import os
import matplotlib.pyplot as pyplot
import logging
import glob
import subprocess as sp
import platform


def get_ffmpeg_path():
    if 'windows' in platform.platform().lower():
        ffmpeg_exe = 'c:\\Program Files (x86)\\ffmpeg-20160531-git-a1953d4-win64-static\\bin\\ffmpeg.exe'
    else:
        ffmpeg_exe = 'ffmpeg'
    return ffmpeg_exe


def init_plot(g, size=(12,12)):
    pyplot.ioff()
    fig = pyplot.figure(figsize=size)
    pyplot.imshow(g, cmap='coolwarm', vmin=0, vmax=10)
    cbar = pyplot.colorbar(ticks=range(0, 11), orientation='horizontal')
    pyplot.tick_params(axis='y', direction='out')
    pyplot.tick_params(axis='x', direction='out')

    return fig


def plot_grid(grid, tick=0, show=False, save=False, fig=None, animated=False):
    if fig is None:
        fig = init_plot()

    pyplot.title = ('Sediment density at time: {}'.format(tick))

    flag = 'CAmovie%s' % str(tick)
    pyplot.imshow(grid, cmap='coolwarm', label=flag, vmin=0, vmax=20, animated=animated)

    if show:
        pyplot.ion()
        pyplot.show()

    if save:
        fig.savefig(os.path.join('tmp_image', "%s.png" % flag))
 #   pyplot.clf()  # clear fig to prevent ticks plots being stored in memory
    return fig



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
    log = logging.getLogger('generate video')
    size_str = '{}x{}'.format(*size)
    command = [ffmpeg_exe, ]
    if video_length is not None:
        command.extend(['-t', '{}'.format(video_length)])
    command.extend([
        '-y',  # (optional) overwrite output file if it exists
        '-r', '{}'.format(fps),  # frames per second
        '-i', os.path.join('tmp_image', 'CAmovie%d.{}'.format(image_format)),
        '-s', size_str,
        '-an',  # Tells FFMPEG not to expect any audio
        '-c:v', 'mjpeg',
        '-pix_fmt', 'yuvj420p',
        '-q', '0',
        '-s', size_str,  # size of one frame
        '{}.avi'.format(video_filename)
    ]
    )
    log.info(' '.join(command))
    try:
        sp.call(command)
    except FileNotFoundError:
        log.error('Could not find FFMPEG executable:\n {}'.format(ffmpeg_exe))
