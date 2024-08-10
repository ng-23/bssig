"""Script for generating images of a object in a scene
with optional image filters applied
"""

import bpy
import argparse
import sys
import os

sys.path.append(os.path.dirname(__file__))

import scene_utils as su
import utils

def get_args_parser():
    parser = argparse.ArgumentParser(description='BSSIG - Blender Synthetic Space Imagery Generator', add_help=True)

    parser.add_argument(
        "space_scene_path",
        metavar="space-scene-path",
        type=str,
        help="Path to space scene to render in Blender",
        )
    
    parser.add_argument(
        'object_path',
        metavar='object-path',
        type=str,
        help='Path to 3D object to render in space scene',
        )
    
    parser.add_argument(
        '--num-images',
        type=int,
        default=10,
        help='Number of images to generate',
        )
    
    parser.add_argument(
        '--object-pos',
        type=float,
        nargs=3,
        default=None,
        help='The x, y, z coordinates of the object if specified. Otherwise, position will be randomly chosen.',
        )
    
    parser.add_argument(
        '--camera-dist', 
        type=float,
        nargs=3,
        default=None, 
        help='The x, y, z distances of the camera from the object if specified. Otherwise, positions will be randomly chosen within a range.',
        )
    
    parser.add_argument(
        '--object-rot', 
        type=float, 
        nargs=3, 
        default=None, 
        help='The x, y, z radians of the object if specified. Otherwise, angles will be randomly chosen within a range.',
        )
    
    parser.add_argument(
        '--camera-rot', 
        type=float, 
        nargs=3, 
        default=None, 
        help='The x, y, z radians of the camera if specified. Otherwise, angles will be randomly chosen within a range.',
        )
    
    parser.add_argument(
        '--min-object-pos', 
        type=float, 
        nargs=3,
        default=[25.0, 25.0, 25.0], 
        help='The minimum x, y, z when randomly choosing position of object.',
        )
    
    parser.add_argument(
        '--max-object-pos', 
        type=float, 
        nargs=3,
        default=[50.0, 50.0, 50.0], 
        help='The maximum x, y, z when randomly choosing position of object.',
        )
    
    parser.add_argument(
        '--min-camera-dist', 
        type=float, 
        nargs=3,
        default=[25.0, 25.0, 25.0], 
        help='The minimum x, y, z when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--max-camera-dist', 
        type=float, 
        nargs=3,
        default=[50.0, 50.0, 50.0], 
        help='The maximum x, y, z when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--min-object-rot', 
        type=float, 
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='The minimum x, y, z radians when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--max-object-rot', 
        type=float, 
        nargs=3,
        default=[360.0, 360.0, 360.0], 
        help='The maximum x, y, z radians when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--min-camera-rot', 
        type=float, 
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='The minimum x, y, z radians when randomly choosing the camera\'s rotation.',
        )
    
    parser.add_argument(
        '--max-camera-rot', 
        type=float,
        nargs=3,
        default=[360.0, 360.0, 360.0], 
        help='The maximum x, y, z radians when randomly choosing the camera\'s rotation.',
        )
    
    parser.add_argument(
        '--min-camera-rot-perturb', 
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='Minimum random perturbation radians for camera rotation.',
        )
    
    parser.add_argument(
        '--max-camera-rot-perturb', 
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='Maximum random perturbation radians for camera rotation.',
        )
    
    parser.add_argument(
        '--focal-len', 
        type=float,
        default=50.0, 
        help='Length of camera lens.',
        )
    
    parser.add_argument(
        '--obj-pos-as-dist', 
        type=str, 
        default='', 
        help='Position the object relative to another in the scene if specified. Otherwise, position is absolute.',
        )
    
    parser.add_argument(
        '--use-cycles',
        action='store_true',
        help='Use Cycles for rendering, otherwise use EEVEE.',
        )
    
    parser.add_argument(
        '--use-gpu', 
        action='store_true', 
        help='Use GPU for rendering. Only applicable when rendering with Cycles. Disables CPU rendering.',
        )
    
    parser.add_argument(
        '--cycles-experimental', 
        action='store_true', 
        help='Use the experimental feature set when rendering with Cycles.',
        )
    
    parser.add_argument('--sun-long', type=float, default=0.0, help='Longitude of the sun. Must have the Sun Position add-on installed.',)

    parser.add_argument('--sun-lat', type=float, default=0.0, help='Latitude of the sun. Must have the Sun Position add-on installed.',)

    parser.add_argument('--date', type=str, default='2024-01-01', help='Global date in yyyy-mm-dd format. Affects sun position only if Sun Position add-on is installed.',)

    parser.add_argument('--utc-time', type=float, default=12.0, help='UTC time. Affects sun position only if Sun Position add-on is installed.',)

    parser.add_argument('--utc-tz', type=float, default=0.0, help='Local UTC time zone. Affects sun position only if Sun Position add-on is installed.',)

    parser.add_argument('--num-horiz-pixels', type=int, default=1920, help='Number of horizontal pixels in generated images.',)
    
    parser.add_argument('--num-vert-pixels', type=int, default=1080, help='Number of vertical pixels in generated images.',)
    
    parser.add_argument('--apply-gauss-blur', type=float, default=None, help='Sigma for Gaussian blurring if specified.',)
    
    parser.add_argument('--apply-gauss-noise', type=float, default=None, help='Variance for Gaussian noise if specified.',)

    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='', 
        help='Path to directory to save images to, or current working directory if not specified.',
        )
    
    return parser

def main():
    parser = get_args_parser()

    args = parser.parse_args(utils.get_script_args())

    if args.output_dir != '':
        utils.mkdir(args.output_dir)

    obj_name = su.setup_scene(args.space_scene_path, args.object_path, focal_len=args.focal_len)

    bpy.context.scene.render.resolution_x = args.num_horiz_pixels
    bpy.context.scene.render.resolution_y = args.num_vert_pixels
    bpy.context.scene.render.resolution_percentage = 100

    if args.use_cycles:
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.feature_set = 'SUPPORTED'
        if args.cycles_experimental:
            bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
        if args.use_gpu:
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
            bpy.context.preferences.addons["cycles"].preferences.get_devices()

            for device in bpy.context.preferences.addons["cycles"].preferences.devices:
                 if device.type == 'GPU':
                    device.use = True
    else:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

    # render loop
    for i in range(args.num_images):
        if args.object_pos is not None:
            if args.obj_pos_as_dist != '':
                su.set_object_dist(obj_name, args.obj_pos_as_dist, args.object_pos)
            else:
                su.set_object_pos(obj_name, args.object_pos)
        else:
            if args.obj_pos_as_dist != '':
                su.rand_set_object_dist(obj_name, args.obj_pos_as_dist, args.min_object_pos, args.max_object_pos)
            else:
                su.rand_set_object_pos(obj_name, args.min_object_pos, args.max_object_pos)
            
        if args.object_rot is not None:
            su.set_object_rot(obj_name, args.object_rot)
        else:
            su.rand_set_object_rot(obj_name, args.min_object_rot, args.max_object_rot)

        if args.camera_dist is not None:
            su.set_camera_dist(obj_name, args.camera_dist)
        else:
            su.rand_set_camera_dist(obj_name, args.min_camera_dist, args.max_camera_dist)

        if args.camera_rot is not None:
            su.set_camera_rot(args.camera_rot)
        else:
            su.rand_set_camera_rot(obj_name, args.min_camera_rot, args.max_camera_rot, min_perturb_vals=args.min_camera_rot_perturb, max_perturb_vals=args.max_camera_rot_perturb)

        bpy.context.scene.render.filepath = os.path.join(args.output_dir, f'img{i}')

        bpy.ops.render.render(write_still=True)

main()
