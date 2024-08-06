"""Script for generating images of a object in a scene
with optional image filters applied
"""

import bpy
import argparse
import scene_utils as su
import utils
import filters

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
        type='str',
        help='Path to 3D object to render in space scene',
        )
    
    parser.add_argument(
        '--num-images',
        type=int,
        default=1000,
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
        default=25.0, 
        help='The minimum x, y, z when randomly choosing position of object.',
        )
    
    parser.add_argument(
        '--max-object-pos', 
        type=float, 
        default=50.0, 
        help='The maximum x, y, z when randomly choosing position of object.',
        )
    
    parser.add_argument(
        '--min-camera-dist', 
        type=float, 
        default=5.0, 
        help='The minimum x, y, z when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--max-camera-dist', 
        type=float, 
        default=10.0, 
        help='The maximum x, y, z when randomly choosing distance of camera from object.',
        )
    
    parser.add_argument(
        '--min-object-rot', 
        type=float, 
        default=0.0, 
        help='The minimum x, y, z radians when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--max-object-rot', 
        type=float, 
        default=360.0, 
        help='The maximum x, y, z radians when randomly choosing the object\'s rotation.',
        )
    
    parser.add_argument(
        '--min-camera-rot', 
        type=float, 
        default=0.0, 
        help='The minimum x, y, z radians when randomly choosing the camera\'s rotation.',
        )
    
    parser.add_argument(
        '--max-camera-rot', 
        type=float, 
        default=360.0, 
        help='The maximum x, y, z radians when randomly choosing the camera\'s rotation.',
        )
    
    parser.add_argument(
        '--min-camera-rot-perturb', 
        type=float, 
        default=0.0, 
        help='Minimum random perturbation for camera rotation.',
        )
    
    parser.add_argument(
        '--max-camera-rot-perturb', 
        type=float, 
        default=0.0, 
        help='Maximum random perturbation for camera rotation.',
        )
    
    parser.add_argument(
        '--obj-pos-as-dist', 
        type=str, 
        default='', 
        help='Position the object relative to another in the scene if specified. Otherwise, position is absolute.',
        )
    
    parser.add_argument(
        '--apply-filters', 
        type=str, 
        nargs='+', 
        default=None, 
        help='Names of post-processing image filters to apply.',
        )
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='', 
        help='Path to directory to save images to, or current working directory if not specified.',
        )

def main():
    parser = get_args_parser()

    args = parser.parse_args()

    utils.mkdir(args.output_dir)

    obj_name = su.setup_scene(args.space_scene_path, args.object_path)

    bpy.context.scene.render.filepath = args.output_dir

    # render loop
    for i in range(len(args.num_images)):
        if args.object_pos is not None:
            if args.obj_pos_as_dist != '':
                su.set_object_dist(obj_name, args.obj_pos_as_dist, args.object_pos)
            else:
                su.set_object_pos(obj_name, args.object_pos)
        else:
            if args.obj_pos_as_dist != '':
                su.rand_set_object_dist(obj_name, args.obj_pos_as_dist, args.min)
            else:
                su.set_object_pos(obj_name, args.object_pos)
            
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
            su.rand_set_camera_rot(obj_name, args.min_camera_rot, args.max_camera_rot, min_perturb_val=args.min_camera_rot_perturb, max_perturb_val=args.max_camera_rot_pertub)

        bpy.ops.render.render(write_still=True)

main()
