import bpy
import random
from mathutils import Euler

def import_object(obj_path:str):
    """Import a single 3D object into the current Blender scene
    """

    curr_objs = set(bpy.data.objects)

    if obj_path.endswith(".obj"):
        bpy.ops.wm.obj_import(filepath=obj_path)
    elif obj_path.endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=obj_path)
    elif obj_path.endswith('.stl'):
        bpy.ops.wm.stl_import(filepath=obj_path)
    else:
        raise Exception('Unknown file format')
    
    imported_objs = set(bpy.data.objects) - curr_objs

    if len(imported_objs) != 1:
        raise Exception('Cannot import more than 1 object')
    
    imported_obj = imported_objs.pop()

    return imported_obj.name
    
def setup_scene(scene_path:str, obj_path:str, focal_len:float, camera_name='Camera'):
    """Loads the scene and imports an object
    """
    
    bpy.ops.wm.open_mainfile(filepath=scene_path)

    obj = import_object(obj_path)

    camera = bpy.data.objects[camera_name]
    camera.data.lens = focal_len

    return obj

def set_object_pos(obj_name:str, xyz):
    """Set an object's position in the scene
    """

    obj = bpy.data.objects[obj_name]

    obj.location = xyz

def set_object_rot(obj_name:str, xyz):
    """Set an object's rotation in the scene
    """
    
    obj = bpy.data.objects[obj_name]

    obj.rotation_euler = xyz

def set_object_dist(obj1_name:str, obj2_name:str, xyz):
    """Set the position of an object relative to another in the scene

    Args:
        obj1: name of an object to set the position of

        ob2_name: name of an object to set the distance to
    """

    obj1, obj2 = bpy.data.objects[obj1_name], bpy.data.objects[obj2_name]

    obj2_x, obj2_y, obj2_z = obj2.location.x, obj2.location.y, obj2.location.z

    obj1.location = (
        obj2_x+xyz[0],
        obj2_y+xyz[1],
        obj2_z+xyz[2],
        )
    
def set_camera_dist(obj_name:str, xyz, camera_name='Camera'):
    """Set the camera's distance from an object in the scene
    """

    set_object_dist(camera_name, obj_name, xyz)

def set_camera_rot(xyz, camera_name='Camera'):
    """Set the camera's rotation in the scene
    """

    set_object_rot(camera_name, xyz)

def rand_xyz(min_vals, max_vals):
    """Randomly generates an (x,y,z) list within a certain range
    """

    xyz = []

    for i in range(3):
        rand_val = random.uniform(min_vals[i], max_vals[i])

        xyz.append(rand_val)

    return xyz

def rand_set_object_pos(obj_name:str, min_vals, max_vals):
    """Randomly set an object's position within a certain range
    """

    xyz = rand_xyz(min_vals, max_vals)

    set_object_pos(obj_name, xyz)

def rand_set_object_rot(obj_name:str, min_vals, max_vals):
    """Randomly set an object's rotation within a certain range
    """

    xyz = rand_xyz(min_vals, max_vals)

    set_object_rot(obj_name, xyz)

def rand_set_object_dist(obj1_name:str, obj2_name:str, min_vals, max_vals):
    """Randomly set the position of an object relative to another within a certain range
    """

    xyz = rand_xyz(min_vals, max_vals)

    set_object_dist(obj1_name, obj2_name, xyz)

def rand_set_camera_dist(target_obj:str, min_vals, max_val:float, camera_name='Camera'):
    """Set the camera's distance from an object within a certain range
    """

    rand_set_object_dist(camera_name, target_obj, min_vals, max_val)

def rand_set_camera_rot(target_obj_name:str, min_rot_vals, max_rot_vals, min_perturb_vals=[0.0,0.0,0.0], max_perturb_vals=[0.0,0.0,0.0], camera_name='Camera'):
    """Randomly set the camera's rotation about an object within a certain range

    Rotation will be in such a way that the target object is always
    at least partially viewable in the camera
    """

    rand_set_object_rot(camera_name, min_rot_vals, max_rot_vals)

    camera = bpy.data.objects[camera_name]

    target = bpy.data.objects[target_obj_name]
    target_loc = target.location

    direction = target_loc - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

    # random perturbation
    xyz = rand_xyz(min_perturb_vals, max_perturb_vals)
    camera.rotation_euler.x += xyz[0] 
    camera.rotation_euler.y += xyz[1]
    camera.rotation_euler.z -= xyz[2]

