"""Module for image filter functions
Filters are implemented using Python and Blender compositor nodes
See https://docs.blender.org/manual/en/latest/compositing/, specifically filter nodes and transform nodes
"""


import scipy as sp
import numpy as np

def apply_gaussian_blur(img:np.array, sigma:float):
    """Applies Gaussian blurring to the image
    """

    return sp.ndimage.gaussian_filter(img, sigma=sigma)

def apply_gaussian_noise(img:np.array, variance:float, mean=0.0):
    """Applies Gaussian noise to the image
    """

    noisy_img = img + np.random.normal(mean, variance, img.shape)

    return np.clip(noisy_img, 0, 255).astype(np.uint8)

def apply_grayscale():
    pass

def apply_lens_flare():
    pass

def apply_flog_glow():
    pass

def apply_motion_blur():
    pass
