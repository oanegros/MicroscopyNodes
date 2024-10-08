import bpy
from bpy.props import (StringProperty, FloatProperty,
                        PointerProperty, IntProperty,
                        BoolProperty, EnumProperty
                        )

# update functions are defined locally
from ..file_to_array import change_path, change_zarr_level, change_channel_ax
from ..ui.channel_list import set_channels

import functools
from operator import attrgetter
import tempfile
from pathlib import Path

print('registering dependent props')

# --- cache dir helpers

CACHE_LOCATIONS = {
    'Temporary' : {
        'icon' : 'FILE_HIDDEN',
        'cache_dir' : functools.partial(tempfile.gettempdir),
        'ui_element': functools.partial(lambda ui_layout : ui_layout.label(text =f'{bpy.context.scene.MiN_cache_dir}', icon="TEMP"))
    },
    'Path' : {
        'icon' : 'FILE_CACHE',
        'cache_dir' : functools.partial(attrgetter('context.scene.MiN_explicit_cache_dir'), bpy),
        'ui_element': functools.partial(lambda ui_layout : ui_layout.prop(bpy.context.scene, "MiN_explicit_cache_dir", text= 'Asset dir'))
    },
    'With Project' : {
        'icon' : 'FILE_BLEND',
        'cache_dir' : functools.partial(bpy.path.abspath, '//'),
        'ui_element' : functools.partial(lambda ui_layout: ui_layout.label(text ='Make sure the project is saved'))
    },
}


def update_cache_dir(self, context):
    bpy.context.scene.MiN_cache_dir = CACHE_LOCATIONS[bpy.context.scene.MiN_selected_cache_option]['cache_dir']()
    

bpy.types.Scene.MiN_input_file = StringProperty(
        name="",
        description="image path, either to tif file, zarr root folder or zarr URL",
        update= change_path,
        options = {'TEXTEDIT_UPDATE'},
        default="",
        maxlen=1024,
        )

bpy.types.Scene.MiN_explicit_cache_dir = StringProperty(
    description = 'Location to store VDB and ABC files, any image data will get RESAVED into blender formats here',
    options = {'TEXTEDIT_UPDATE'},
    default = str(Path('~', '.microscopynodes').expanduser()),
    subtype = 'DIR_PATH',
    update = update_cache_dir
    )

bpy.types.Scene.MiN_selected_cache_option = StringProperty(
        name="",
        description="Where VDB and ABC files are created",
        default= "Temporary",
        update= update_cache_dir
        )


bpy.types.Scene.MiN_axes_order = StringProperty(
        name="",
        description="axes order (out of tzcyx)",
        default="",
        update=change_channel_ax,
        maxlen=6)

bpy.types.Scene.MiN_selected_zarr_level = StringProperty(
        name="",
        description="Selected zarr level/dataset",
        update= change_zarr_level,
        default= ""
        )

bpy.types.Scene.MiN_channel_nr = IntProperty(
        name = "", 
        default = 0,
        update = set_channels,
        )

def poll_empty(self, object):
    from ..load_components.load_generic import get_min_gn
    if object.type != 'EMPTY':
        return False
    if any([get_min_gn(child) != None for child in object.children]):
        return True
    return False

bpy.types.Scene.MiN_reload = PointerProperty(
        name = "", 
        description = "Reload data of Microscopy Nodes object.\nCan be used to replace deleted (temp) files, change resolution, or channel settings.\nUsage: Point to previously loaded microscopy data.",
        type=bpy.types.Object,
        poll=poll_empty,
        )
        