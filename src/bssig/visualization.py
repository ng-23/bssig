import filters
import os
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def plot_img_histogram(img:np.ndarray, to_grayscale=True, title='Image Histogram', log_scale=True, save=True, show=False, output_dir='', filename='img_hist'):
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

    plt.title(title)
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Pixel Frequency')

    if save:
        plt.savefig(os.path.join(output_dir,filename))

    if show:
        plt.show()

    plt.close()

def plot_ssim_histogram(ssims:pd.DataFrame, bins:str|int|None=None, title='SSIM Scores Histogram', save=True, show=False, output_dir='', filename='ssim_hist'):
    plt.hist(ssims['ssim'], bins=bins, color='red', edgecolor='black')
    plt.title(title)
    plt.xlabel('SSIM Score')
    plt.ylabel('Frequency')
    
    if save:
        plt.savefig(os.path.join(output_dir,filename))

    if show:
        plt.show()

    plt.close()

def plot_ssim_boxplot(ssims:pd.DataFrame, title='SSIM Scores Boxplot', save=True, show=False, output_dir='', filename='ssim_boxplot'):
    plt.boxplot(ssims['ssim'],patch_artist=True)
    plt.title(title)
    plt.ylabel('SSIM Score')
    
    if save:
        plt.savefig(os.path.join(output_dir,filename))

    if show:
        plt.show()

    plt.close()