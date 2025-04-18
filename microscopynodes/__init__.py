# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Parts of this are based on or taken from Brady Johnston's MolecularNodes
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

from . import file_to_array
from . import ui

from . import min_nodes
from .min_nodes.shader_nodes import MIN_add_shader_node_menu, MIN_context_shader_node_menu
from .ui.preferences import addon_preferences


all_classes = (
    ui.CLASSES +
    file_to_array.CLASSES +
    min_nodes.CLASSES
)

# print(all_classes)
def _test_register():
    try:
        register()
    except Exception:
        unregister()
        register()
        pass


def register():
    for op in all_classes:
        try:
            bpy.utils.register_class(op)
        except Exception as e:
            print(op, e)
            pass
    bpy.types.Scene.MiN_array_options = bpy.props.CollectionProperty(type=file_to_array.ArrayOption)
    bpy.types.Scene.MiN_channelList = bpy.props.CollectionProperty(type=ui.channel_list.ChannelDescriptor)
    bpy.types.NODE_MT_add.append(MIN_add_shader_node_menu)
    bpy.types.NODE_MT_context_menu.append(MIN_context_shader_node_menu)
    try: 
        addon_preferences(bpy.context).channels[0].name
    except:
        try:
            addon_preferences(bpy.context).n_default_channels = 6
        except AttributeError:
            pass
    return

def unregister():
    for op in all_classes:
        try:
            bpy.utils.unregister_class(op)
        except Exception as e:
            print(op, e)
            pass
    bpy.types.NODE_MT_add.remove(MIN_add_shader_node_menu)
    bpy.types.NODE_MT_context_menu.remove(MIN_context_shader_node_menu)

