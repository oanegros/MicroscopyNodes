import bpy
import numpy as np
from pathlib import Path

from .ui import preferences
from .handle_blender_structs import *
from .file_to_array import load_array, selected_array_option
from .ui.preferences import addon_preferences


def get_cache_dir():
    if addon_preferences().cache_option == 'TEMPORARY':
        path = tempfile.gettempdir()
    if addon_preferences().cache_option == 'PATH':
        path = addon_preferences().cache_path
    if addon_preferences().cache_option == 'WITH_PROJECT':
        path = bpy.path.abspath('//')
    path = Path(path) / Path(bpy.context.scene.MiN_input_file).stem 
    path = path / str(bpy.context.scene.MiN_selected_array_option)
    path.mkdir(parents=True, exist_ok=True)
    return path

def parse_initial():
    # all parameters initialized here are shared between threaded and blocking load functions
    check_input()
    axes_order = bpy.context.scene.MiN_axes_order
    pixel_size = np.array([bpy.context.scene.MiN_xy_size,bpy.context.scene.MiN_xy_size,bpy.context.scene.MiN_z_size])
    if not bpy.context.scene.MiN_pixel_sizes_are_rescaled: 
        pixel_size *= selected_array_option().scale() 
    cache_dir = get_cache_dir() 

    ch_dicts = parse_channellist(bpy.context.scene.MiN_channelList)
    size_px = np.array([selected_array_option().shape()[axes_order.find(dim)] if dim in axes_order else 0 for dim in 'xyz'])
    size_px = tuple([max(ax, 1) for ax in size_px])

    if bpy.context.scene.MiN_reload is None:
        bpy.context.scene.MiN_update_data = True
        bpy.context.scene.MiN_update_settings = True
    return ch_dicts, (axes_order,  pixel_size, size_px), cache_dir

def parse_channellist(channellist):
    # initializes ch_dicts, which holds data and metadata, such as user settings, per channel
    ch_dicts = []
    for channel in bpy.context.scene.MiN_channelList:
        ch_dicts.append({k:getattr(channel,k) for k in channel.keys()}) # take over settings from UI - uses getattr to get enum names
        for key in min_keys: # rename ui-keys to enum for which objects to load
            if key.name.lower() in ch_dicts[-1]:
                ch_dicts[-1][key] = ch_dicts[-1][key.name.lower()]
        ch_dicts[-1]['identifier'] = f"ch_id{channel['ix']}" # reload-identity
        ch_dicts[-1]['data'] = None
        ch_dicts[-1]['collections'] = {}
        ch_dicts[-1]['metadata'] = {}
        ch_dicts[-1]['local_files'] = {}
        ch_dicts[-1]['surf_resolution'] = int(addon_preferences(bpy.context).surf_resolution)
    return ch_dicts

def parse_unit(string):
    if string == "ANGSTROM":
        return 1e-10
    if string == "NANOMETER":
        return 1e-9
    if string == "MICROMETER":
        return 1e-6
    if string == "MILLIMETER":
        return 1e-3
    if string == "METER":
        return 1

def parse_scale(size_px, pixel_size, objs):
    scale = None
    scale_factor = 1
        
    world_scale = addon_preferences(bpy.context).import_scale
    isotropic = np.array([1,1,pixel_size[-1]/pixel_size[0]]) 
    if world_scale == "DEFAULT" or bpy.context.scene.MiN_unit == 'AU': # cm / px
        scale = isotropic*0.01
    
    if world_scale == "MOLECULAR_NODES": # cm / nm
        physical_size = parse_unit(bpy.context.scene.MiN_unit) * pixel_size
        scale = physical_size / 1e-7
    if "_SCALE" in world_scale:
        physical_size = parse_unit(bpy.context.scene.MiN_unit) * pixel_size
        scale = physical_size / parse_unit(world_scale.removesuffix("_SCALE")) 

    if objs[min_keys.AXES] is not None:
        old_size_px, old_scale = get_previous_scale(objs[min_keys.AXES], size_px)
        if bpy.context.scene.MiN_update_data and not bpy.context.scene.MiN_update_settings:
            scale = (np.array(old_size_px) / np.array(size_px)) * old_scale
        scale_factor = (np.array(size_px) / np.array(old_size_px)) * (scale / old_scale)
    return scale, scale_factor
    

def get_previous_scale(axes_obj, size_px):
    try:
        mod = get_min_gn(axes_obj)
        nodes = mod.node_group.nodes
        old_size_px = nodes['[Microscopy Nodes size_px]'].vector
        old_scale = nodes['[Microscopy Nodes scale]'].vector
        return old_size_px, old_scale
    except KeyError as e:
        print(e)
        pass


def parse_loc(scale, size_px, container):
    if not bpy.context.scene.MiN_update_settings:
        try:
            return container.location
        except Exception as e:
            pass
    prefloc = addon_preferences(bpy.context).import_loc
    if prefloc == "XY_CENTER":
        return [-0.5,-0.5,0] * np.array(size_px) * scale 
    if prefloc == "XYZ_CENTER":
        return [-0.5,-0.5,-0.5] * np.array(size_px) * scale 
    if prefloc == "ZERO":
        return [0, 0, 0] * np.array(size_px) * scale 



def check_input():
    if bpy.context.scene.MiN_xy_size <= 0  or bpy.context.scene.MiN_z_size <= 0:
        raise ValueError("cannot do zero-size pixels")
    # TODO change this to a callback function on change channel name instead
    ch_names = [ch["name"] for ch in bpy.context.scene.MiN_channelList]
    if len(set(ch_names)) < len(ch_names):
        raise ValueError("No duplicate channel names allowed")
    return

def parse_reload(container_obj):
    objs = {}
    for key in min_keys:
        objs[key] = None
        if container_obj is not None:
            for child in container_obj.children:
                if get_min_gn(child) is not None and key.name.lower() in get_min_gn(child).name:
                    objs[key] = child

    return objs

