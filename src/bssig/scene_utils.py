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
    
def setup_scene(scene_path:str, obj_path:str):
    """Loads the scene and imports an object
    """
    
    bpy.ops.wm.open_mainfile(filepath=scene_path)

    obj = import_object(obj_path)

    return obj

def set_object_pos(obj:str, xyz):
    """Set an object's position in the scene
    """

    obj = bpy.data.objects[obj]

    obj.location = xyz

def set_object_rot(obj:str, xyz):
    """Set an object's rotation in the scene
    """
    
    obj = bpy.data.objects[obj]

    obj.rotation_euler = xyz

def set_object_dist(obj1:str, obj2:str, xyz):
    """Set the position of an object relative to another in the scene

    Args:
        obj1: name of an object to set the position of

        ob2_name: name of an object to set the distance to
    """

    obj1, obj2 = bpy.data.objects[obj1], bpy.data.objects[obj2]

    obj2_x, obj2_y, obj2_z = obj2.location.x, obj2.location.y, obj2.location.z

    obj1.location = (
        obj2_x+xyz[0],
        obj2_y+xyz[1],
        obj2_z+xyz[2],
        )

def set_camera_dist(obj:str, xyz, camera_name='Camera'):
    """Set the camera's distance from an object in the scene
    """

    set_object_dist(camera_name, obj, xyz)

def set_camera_rot(xyz, camera_name='Camera'):
    """Set the camera's rotation in the scene
    """

    set_object_rot(camera_name, xyz)

def rand_xyz(min_val:float, max_val:float):
    """Randomly generates an (x,y,z) tuple within a certain range
    """

    xyz = []

    for _ in range(3):
        rand_val = random.uniform(min_val, max_val)

        xyz.append(rand_val)

    return xyz

def rand_set_object_pos(obj:str, min_val:float, max_val:float):
    """Randomly set an object's position within a certain range
    """

    xyz = rand_xyz(min_val, max_val)

    set_object_pos(obj, xyz)

def rand_set_object_rot(obj:str, min_val:float, max_val:float):
    """Randomly set an object's rotation within a certain range
    """

    xyz = rand_xyz(min_val, max_val)

    set_object_rot(obj, xyz)

def rand_set_object_dist(obj1:str, obj2:str, min_val:float, max_val:float):
    """Randomly set the position of an object relative to another within a certain range
    """

    xyz = rand_xyz(min_val, max_val)

    set_object_dist(obj1, obj2, xyz)

def rand_set_camera_dist(target_obj:str, min_val:float, max_val:float, camera_name='Camera'):
    """Set the camera's distance from an object within a certain range
    """

    rand_set_object_dist(camera_name, target_obj, min_val, max_val)

def rand_set_camera_rot(target_obj:str, min_rot_val:float, max_rot_val:float, min_perturb_val=0.0, max_perturb_val=0.0, camera_name='Camera'):
    """Randomly set the camera's rotation about an object within a certain range

    Rotation will be in such a way that the target object is always
    at least partially viewable in the camera
    """

    rand_set_object_rot(camera_name, min_rot_val, max_rot_val)

    camera = bpy.data.objects[camera_name]

    target = bpy.data.objects[target_obj]
    target_loc = target.location

    direction = target_loc - camera.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

    perturb = Euler(
        (
        random.uniform(min_perturb_val, max_perturb_val),
        random.uniform(min_perturb_val, max_perturb_val),
        random.uniform(min_perturb_val, max_perturb_val),
        ), 'XYZ',)
    camera.rotation_euler.rotate(perturb)

