"""Script for validating the quality of images
"""

import argparse
import sys
import os
import random
import skimage
import json
import pandas as pd
from skimage import img_as_float

sys.path.append(os.path.dirname(__file__))

import utils
import visualization as viz

def get_args_parser():
    parser = argparse.ArgumentParser(description='Image Quality Validation', add_help=True)

    parser.add_argument(
        'synth_images_path',
        metavar='synth-images-path',
        type=str,
        help='Path to synthetic images to validate.',
        )
    
    parser.add_argument(
        'ref_images_path',
        metavar='ref-images-path',
        type=str,
        help='Path to reference images to validate against.',
        )
    
    parser.add_argument(
        '--grayscale-synth', 
        action='store_true', 
        help='Apply grayscale filter to synthetic images before validation.',
        )
    
    parser.add_argument(
        '--grayscale-ref', 
        action='store_true', 
        help='Apply grayscale filter to reference images before validating against.',
        )
    
    parser.add_argument(
        '--calc-ssim', 
        type=str,
        choices=['standard','best-match'],
        default='standard',
        help='''SSIM calculation method. Saved as a CSV.
        standard - Calculates the SSIM between corresponding pairs of synthetic and reference images. Must have same amount of synthetic and reference images.
        best-match - Calculates the SSIM between all possible pairs of synthetic and reference images, storing the best (highest) one.''',
        )
    
    parser.add_argument('--ssim-hist', action='store_true', help='Generate a histogram of SSIMs.',)

    parser.add_argument('--ssim-boxplot', action='store_true', help='Generate a boxplot of SSIMs.',)

    parser.add_argument('--use-n-rand-imgs', type=int, default=None, help='If specified, n random synthetic/reference images will be chosen for comparison.',)
    
    parser.add_argument('--seed', type=int, default=None, help='RNG seed. Only applies when choosing a random subset of synthetic/reference images.',)

    parser.add_argument('--save-cmd-args', action='store_true', help='Save the command line arguments used.',)

    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='', 
        help='Path to directory to save results to, or current working directory if not specified.',
        )
    
    return parser

def load_images(filepath:str, n_rand=None):
    img_paths = sorted([entry.path for entry in os.scandir(filepath) if entry.is_file()])
    if n_rand is not None:
        if n_rand > len(img_paths):
            raise Exception(f'{filepath} only contains {len(img_paths)} images, cannot randomly choose {n_rand}')
        img_paths = random.sample(img_paths, n_rand)

    imgs = []
    for path in img_paths:
        imgs.append(img_as_float(skimage.io.imread(path)))

    img_mapping = {i:os.path.basename(img_paths[i]) for i in range(len(img_paths))}

    return imgs, img_mapping

def calc_ssims(synth_imgs, synth_imgs_map:dict, ref_imgs, ref_imgs_map:dict, to_grayscale=None, save=True, output_dir='', filename='ssims.csv'):
    if len(synth_imgs) != len(ref_imgs):
        raise Exception(f'Unequal number of synthetic and reference images: {len(synth_imgs)} and {len(ref_imgs)}')
    
    res = {}
    
    for i in range(len(ref_imgs)):
        ssim = utils.calc_ssim(synth_imgs[i], ref_imgs[i], to_grayscale=to_grayscale)
        res[i] = [synth_imgs_map[i], ref_imgs_map[i], ssim]

    df = pd.DataFrame.from_dict(data=res, orient='index', columns=['synth_img','ref_img','ssim'])

    if save:
        df.to_csv(os.path.join(output_dir,filename))
        
    return df

def calc_ssims_best_match(synth_imgs, synth_imgs_map:dict, ref_imgs, ref_imgs_map:dict, to_grayscale=None, save=True, output_dir='', filename='ssims_best_match.csv'):
    res = {}

    for i in range(len(synth_imgs)):
        best_match_img, best_match_ssim = None, 0.0
        print(f'synth img {i}')

        for j in range(len(ref_imgs)):
            ssim = utils.calc_ssim(synth_imgs[i], ref_imgs[j], to_grayscale=to_grayscale)

            if best_match_img is None or ssim > best_match_ssim:
                best_match_img = ref_imgs_map[j]
                best_match_ssim = ssim

        res[i] = [synth_imgs_map[i], best_match_img, best_match_ssim]

    df = pd.DataFrame.from_dict(data=res, orient='index', columns=['synth_img','ref_img','ssim'])

    if save:
        df.to_csv(os.path.join(output_dir,filename))
        
    return df

def main():
    parser = get_args_parser()

    args = parser.parse_args()

    if args.output_dir != '':
        utils.mkdir(args.output_dir)

    with open(os.path.join(args.output_dir, 'cmd_args.json'), "w") as f:
        json.dump(vars(args), f)

    random.seed(args.seed)

    synth_imgs, synth_imgs_map = load_images(args.synth_images_path, n_rand=args.use_n_rand_imgs)
    ref_imgs, ref_imgs_map = load_images(args.ref_images_path, n_rand=args.use_n_rand_imgs)

    to_grayscale = None
    if args.grayscale_synth:
        to_grayscale = 'img1'
    if args.grayscale_ref:
        if to_grayscale is not None:
            to_grayscale = 'both'
        else:
            to_grayscale = 'img2'

    ssims = None
    if args.calc_ssim == 'standard':
        ssims = calc_ssims(synth_imgs, synth_imgs_map, ref_imgs, ref_imgs_map, to_grayscale=to_grayscale, output_dir=args.output_dir)
    elif args.calc_ssim == 'best-match':
        ssims = calc_ssims_best_match(synth_imgs, synth_imgs_map, ref_imgs, ref_imgs_map, to_grayscale=to_grayscale, output_dir=args.output_dir)

    print(ssims)

    if args.ssim_hist:
        viz.plot_ssim_histogram(ssims, output_dir=args.output_dir)

    if args.ssim_boxplot:
        viz.plot_ssim_boxplot(ssims, output_dir=args.output_dir)

main()