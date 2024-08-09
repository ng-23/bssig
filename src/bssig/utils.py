import os
import errno
import sys
import filters
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from skimage.metrics import structural_similarity as ssim

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

def calc_ssim(img1:np.ndarray, img2:np.ndarray, to_grayscale=True):
    """Calculates the Structural Similarity Index (SSIM) between 2 images

    Args:
        img1: matrix representation of 1st image

        img2: matrix representation of 2nd image

        to_grayscale: convert images to grayscale, otherwise assume they're already gray scale
    """

    if to_grayscale:
        img1 = filters.apply_grayscale(img1)
        img2 = filters.apply_grayscale(img2)

    # find min and max pixel values across both images
    min_value = min(np.min(img1), np.min(img2))
    max_value = max(np.max(img1), np.max(img2))

    # calculate range of pixel values (ssim can break if you don't specify this)
    data_range = max_value - min_value

    return ssim(img1, img2, data_range=data_range)

def plot_img_histogram(img:np.ndarray, to_grayscale=True, log_scale=True, save=True, show=False, filename='img_hist'):
    """Plots the pixel intensity histogram of an image
    """
    
    if to_grayscale:
        img = filters.apply_grayscale(img)

    plt.hist(img.flatten(), bins=256, range=(0.0, 1.0), log=log_scale)

    cbar = plt.colorbar(mpl.cm.ScalarMappable(
        norm=mpl.colors.Normalize(0,1), 
        cmap=mpl.cm.get_cmap('gray', 256)), 
        ax=plt.gca(),
        )
    cbar.set_label('Grayscale Intensity')

    plt.title('Image Histogram')
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Pixel Frequency')

    if save:
        plt.savefig(filename)

    if show:
        plt.show()

    plt.close()

