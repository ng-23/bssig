import os
import errno
import sys
import filters
import numpy as np
from skimage import img_as_float
from skimage.metrics import structural_similarity as ssim
from dataclasses import dataclass

@dataclass
class CameraSettings:
    name = 'Camera'
    focal_len = 50.0
    track_axis = 'TRACK_NEGATIVE_Z'
    up_axis = 'UP_Y'

@dataclass
class RenderSettings:
    num_horiz_pixels=1920
    num_vert_pixels=1080
    resolution_perc = 100
    use_cycles = False
    cycles_experimental = False
    cycles_device_type = None
    use_gpu = False
    num_render_samples = 200

@dataclass
class SunSettings:
    name = 'Sun'
    track_axis = 'TRACK_NEGATIVE_Z'
    up_axis = 'UP_Y'

    
def parser_camera_settings(args):
    camera_settings = CameraSettings()

    camera_settings.focal_len = args.focal_len
    
    return camera_settings

def parse_render_settings(args):
    render_settings = RenderSettings()

    render_settings.num_horiz_pixels = args.num_horiz_pixels
    render_settings.num_vert_pixels = args.num_vert_pixels
    render_settings.use_cylces = args.use_cycles
    render_settings.cycles_experimental = args.cycles_experimental
    render_settings.cycles_device_type = args.cycles_device_type
    render_settings.use_gpu = args.use_gpu
    render_settings.num_render_samples = args.num_render_samples

    return render_settings

def parse_sun_settings(args):
    sun_settings = SunSettings()

    return sun_settings
    
def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def get_script_args():
    # taken frome https://blender.stackexchange.com/questions/6817/how-to-pass-command-line-arguments-to-a-blender-python-script
    
    argv = sys.argv
    try:
        index = argv.index("--") + 1
    except ValueError:
        index = len(argv)

    argv = argv[index:]

    return argv

def calc_ssim(img1:np.ndarray, img2:np.ndarray, to_grayscale='both'):
    """Calculates the Structural Similarity Index (SSIM) between 2 images

    Args:
        img1: matrix representation of 1st image

        img2: matrix representation of 2nd image

        to_grayscale: convert 1, both, or none of the images to grayscale, otherwise assume they're already grayscale
    """

    # normalize pixel values to be in range 0-1
    img1 = img_as_float(img1)
    img2 = img_as_float(img2)

    if to_grayscale is not None:
        if to_grayscale == 'both':
            img1 = filters.apply_grayscale(img1)
            img2 = filters.apply_grayscale(img2)
        elif to_grayscale == 'img1':
            img1 = filters.apply_grayscale(img1)
        elif to_grayscale == 'img2':
            img2 = filters.apply_grayscale(img2)
        else:
            raise Exception('Invalid value for to_grayscale - support values are None, img1, img2')

    return ssim(img1, img2, data_range=1.0)

