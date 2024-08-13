"""Script for generating images of an object in a scene
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
        '--reference-object', 
        type=str, 
        default='', 
        help='Name of an object already in the scene to position the imported object relative to. Otherwise, position is absolute.',
        )
    
    parser.add_argument(
        '--object-dist', 
        type=float, 
        default=None, 
        help='Distance of imported object relative to object already in scene. Distance randomly chosen within a sphere centered around other object if unspecified.',
        )
    
    parser.add_argument(
        '--object-pos', 
        type=float, 
        nargs=3, 
        default=None, 
        help='Absolute x, y, z position of imported object in scene. Randomly chosen within a certain range if unspecified.',
        )
    
    parser.add_argument(
        '--camera-dist', 
        type=float,
        nargs=3,
        default=None, 
        help='The x, y, z distances of the camera from the object if specified. Otherwise, distance will be chosen randomly within a sphere centered around the target.',
        )
    
    parser.add_argument(
        '--object-rot', 
        type=float, 
        nargs=3, 
        default=None, 
        help='The x, y, z rotations of the object if specified. Otherwise, rotation will be randomly chosen.',
        )
    
    parser.add_argument(
        '--camera-rot', 
        type=float, 
        nargs=3, 
        default=None, 
        help='The x, y, z rotations of the camera if specified. Otherwise, rotation will be randomly chosen.',
        )
    
    parser.add_argument(
        '--min-object-pos', 
        type=float, 
        nargs=3,
        default=[25.0, 25.0, 25.0], 
        help='The minimum x, y, z when randomly choosing absolute position of object.',
        )
    
    parser.add_argument(
        '--max-object-pos', 
        type=float, 
        nargs=3,
        default=[50.0, 50.0, 50.0], 
        help='The maximum x, y, z when randomly choosing absolute position of object.',
        )
    
    parser.add_argument(
        '--min-object-dist', 
        type=float, 
        default=5.0, 
        help='Minimum distance of object when positioning imported object relative to exisiting one.',
        )

    parser.add_argument(
        '--max-object-dist', 
        type=float, 
        default=25.0, 
        help='Maximum distance of object when positioning imported object relative to existing one.',
        )
    
    parser.add_argument(
        '--min-camera-dist', 
        type=float, 
        default=5.0, 
        help='The minimum distance when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--max-camera-dist', 
        type=float, 
        default=25.0, 
        help='The maximum distance when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--min-object-rot', 
        type=float, 
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='The minimum x, y, z rotations when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--max-object-rot', 
        type=float, 
        nargs=3,
        default=[360.0, 360.0, 360.0], 
        help='The maximum x, y, z rotations when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--min-camera-rot-perturb', 
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='Minimum random perturbation x, y, z rotations for camera rotation.',
        )
    
    parser.add_argument(
        '--max-camera-rot-perturb', 
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0], 
        help='Maximum random perturbation x, y, z rotations for camera rotation.',
        )
        
    parser.add_argument(
        '--sun-dist', 
        type=float, 
        default=5000, 
        help='Distance of the sun object from the origin of the scene.',
        )

    parser.add_argument(
        '--focal-len', 
        type=float,
        default=50.0, 
        help='Length of camera lens.',
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
        '--cycles-device-type', 
        type=str, 
        default=None, 
        help='Device to use for rendering with Cycles.',
        )
    
    parser.add_argument(
        '--cycles-experimental', 
        action='store_true', 
        help='Use the experimental feature set when rendering with Cycles.',
        )

    parser.add_argument('--num-render-samples', type=int, default=200, help='Number of samples during rendering.',)

    parser.add_argument('--num-horiz-pixels', type=int, default=1920, help='Number of horizontal pixels in generated images.',)
    
    parser.add_argument('--num-vert-pixels', type=int, default=1080, help='Number of vertical pixels in generated images.',)

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

    camera_settings, render_settings, sun_settings = utils.parser_camera_settings(args), utils.parse_render_settings(args), utils.parse_sun_settings(args)
    
    obj_name = su.setup_scene(args.space_scene_path, args.object_path, camera_settings, render_settings, sun_settings)

    # render loop
    for i in range(args.num_images):
        if args.reference_object:
            # distance positioning
            if args.object_dist is not None:
                # static distance
                su.set_object_dist(
                    obj_name, 
                    args.reference_object, 
                    args.object_dist,
                    )
            else:
                # random distance
                su.rand_set_object_dist(
                    obj_name, 
                    args.reference_object, 
                    args.min_object_dist, 
                    args.max_object_dist,
                    )
        else:
            # absolute positioning
            if args.object_pos is not None:
                # static absolute position
                su.set_object_pos(obj_name, args.object_pos,)
            else:
                # random absolute position
                su.rand_set_object_pos(
                    obj_name, 
                    args.min_object_pos, 
                    args.max_object_pos,
                    )
        
        if args.object_rot is not None:
            su.set_object_rot(obj_name, args.object_rot)
        else:
            su.rand_set_object_rot(
                obj_name, 
                args.min_object_rot, 
                args.max_object_rot,
                )
            
        su.rand_set_sun_pos(args.sun_dist)

        if args.camera_dist is not None:
            su.set_object_dist(
                camera_settings.name, 
                obj_name, 
                args.camera_dist,
                )
        else:
            su.rand_set_object_dist(
                camera_settings.name,
                obj_name, 
                args.min_camera_dist, 
                args.max_camera_dist,
                )

        if args.camera_rot is not None:
            su.set_object_rot(camera_settings.name, args.camera_rot)
        else:
            su.rand_set_camera_perturb(
                camera_name=camera_settings.name,
                min_xyz_perturbs=args.min_camera_rot_perturb, 
                max_xyz_perturbs=args.max_camera_rot_perturb,
                )

        bpy.context.scene.render.filepath = os.path.join(args.output_dir, f'img{i}')

        bpy.ops.render.render(write_still=True)

main()
