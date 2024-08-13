import bpy
import random
import math
from utils import CameraSettings, RenderSettings, SunSettings

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
        raise Exception('Unknown/unsupported file format')
    
    imported_objs = set(bpy.data.objects) - curr_objs

    if len(imported_objs) != 1:
        raise Exception('Cannot import more than 1 object')
    
    imported_obj = imported_objs.pop()

    return imported_obj.name
    
def setup_scene(scene_path:str, obj_path:str, camera_settings:CameraSettings, render_settings:RenderSettings, sun_settings:SunSettings):
    """Loads the scene and imports an object
    """
    
    bpy.ops.wm.open_mainfile(filepath=scene_path)

    obj_name = import_object(obj_path)

    camera = bpy.data.objects[camera_settings.name]
    camera.data.lens = camera_settings.focal_len
    camera.constraints.new(type='TRACK_TO')
    camera.constraints['Track To'].target = bpy.data.objects[obj_name]
    camera.constraints['Track To'].track_axis = camera_settings.track_axis
    camera.constraints['Track To'].up_axis = camera_settings.up_axis

    sun = bpy.data.objects[sun_settings.name]
    sun.constraints.new(type='TRACK_TO')
    sun.constraints['Track To'].target = bpy.data.objects['Earth'] # always point the sun towards the earth
    sun.constraints['Track To'].track_axis = camera_settings.track_axis
    sun.constraints['Track To'].up_axis = camera_settings.up_axis

    bpy.context.scene.render.resolution_x = render_settings.num_horiz_pixels
    bpy.context.scene.render.resolution_y = render_settings.num_vert_pixels
    bpy.context.scene.render.resolution_percentage = render_settings.resolution_perc

    if render_settings.use_cycles:
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.feature_set = 'SUPPORTED'
        bpy.context.scene.cycles.samples = render_settings.num_render_samples
        if render_settings.cycles_experimental:
            bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
        if render_settings.use_gpu:
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = render_settings.cycles_device_type
            bpy.context.preferences.addons["cycles"].preferences.get_devices()

            for device in bpy.context.preferences.addons["cycles"].preferences.devices:
                 if device.type == 'GPU':
                    device.use = True
    else:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        bpy.context.scene.eevee.taa_render_samples = render_settings.num_render_samples

    return obj_name

def set_sun_pos(dist_from_origin:float, angle:float, sun_name='Sun'):
    """Set the sun's position on the ecliptic plane
    
    Assumes scene is an ECI frame
    """
    
    # calculate x and y positions based on the angle and distance
    x = dist_from_origin * math.cos(angle)
    y = dist_from_origin * math.sin(angle)
    z = 0  # ecliptic plane has z = 0
    
    set_object_pos(sun_name, [x,y,z])

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

def set_object_dist(reposition_obj_name:str, static_obj_name:str, xyz):
    """Set the position of an object relative to another in the scene
    """

    obj1, obj2 = bpy.data.objects[reposition_obj_name], bpy.data.objects[static_obj_name]

    obj2_x, obj2_y, obj2_z = obj2.location.x, obj2.location.y, obj2.location.z

    obj1.location = (
        obj2_x+xyz[0],
        obj2_y+xyz[1],
        obj2_z+xyz[2],
        )

def rand_xyz(min_vals, max_vals):
    """Randomly generates an (x,y,z) list within a certain range
    """

    xyz = []

    for i in range(3):
        rand_val = random.uniform(min_vals[i], max_vals[i])

        xyz.append(rand_val)

    return xyz

def rand_cartesian_coords(min_val:float, max_val:float):
    radius = random.uniform(min_val, max_val)

    # generate random spherical coordinates
    theta = random.uniform(0, 2 * math.pi)  # random angle around
    phi = random.uniform(0, math.pi)        # random inclination angle

    # convert spherical coordinates to Cartesian coordinates
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.sin(phi) * math.sin(theta)
    z = radius * math.cos(phi)

    return [x,y,z]

def rand_set_sun_pos(dist_from_origin:float, sun_name='Sun'):
    """Randomly set the sun's position along the ecliptic plane
    """

    angle = random.uniform(0, 2*math.pi)

    set_sun_pos(dist_from_origin, angle, sun_name=sun_name)

def rand_set_object_pos(obj_name:str, min_xyz_pos, max_xyz_pos):
    """Randomly set an object's absolute position within a certain range
    """

    xyz = rand_xyz(min_xyz_pos, max_xyz_pos)

    set_object_pos(obj_name, xyz)

def rand_set_object_rot(obj_name:str, min_vals, max_vals):
    """Randomly set an object's rotation within a certain range
    """

    xyz = rand_xyz(min_vals, max_vals)

    set_object_rot(obj_name, xyz)

def rand_set_object_dist(reposition_obj_name:str, static_obj_name:str, min_dist:float, max_dist:float):
    """Randomly set the position of an object relative to another

    Distance is chosen randomly within a sphere centered around the object
    """

    xyz = rand_cartesian_coords(min_dist, max_dist)

    set_object_dist(reposition_obj_name, static_obj_name, xyz)

def rand_set_camera_perturb(camera_name='Camera', min_xyz_perturbs=[0.0,0.0,0.0], max_xyz_perturbs=[0.0,0.0,0.0]):
    """Randomly perturb the camera's rotation about an object within a certain range

    It is assumed that the camera specified is already set to track the target object, thus the target object's name cannot be specified when calling
    """

    camera = bpy.data.objects[camera_name]

    xyz = rand_xyz(min_xyz_perturbs, max_xyz_perturbs)
    camera.rotation_euler.x += xyz[0] 
    camera.rotation_euler.y += xyz[1]
    camera.rotation_euler.z -= xyz[2]

