from . import cmap_menus
from .nodeVolumeAlpha import volume_alpha_node
from .handle_cmap import set_color_ramp, get_lut
from .nodeRemapObjectID import remap_oid_node
from . import ops
import bpy


class MIN_MT_CMAP_ADD(bpy.types.Menu):
    bl_idname = "MIN_MT_CMAP_ADD"
    bl_label = "Add LUT"

    def draw(self, context):
        cmap_menus.draw_category_menus(self, context, "microscopynodes.add_lut")

class MIN_MT_CMAP_REPLACE(bpy.types.Menu):
    bl_idname = "MIN_MT_CMAP_REPLACE"
    bl_label = "Replace LUT"

    def draw(self, context):
        cmap_menus.draw_category_menus(self, context, "microscopynodes.add_lut")



def MIN_add_shader_node_menu(self, context):
    if "ShaderNodeTree" == bpy.context.area.spaces[0].tree_type:
        layout = self.layout
        layout.menu("MIN_MT_CMAP_ADD", text="LUTs", icon="COLOR")
    elif context.area.ui_type == 'ShaderNodeTree' and bpy.context.area.type == "NODE_EDITOR":
        if len(bpy.context.selected_nodes) == 1 and bpy.context.selected_nodes[0].type == 'VALTORGB':
            layout = self.layout
            layout.menu("MIN_MT_CMAP_REPLACE", text="Replace LUT", icon="COLOR")
            layout.operator("microscopynodes.replace_lut", text="Reverse LUT", icon="LOOP_BACK")


CLASSES = [MIN_MT_CMAP_ADD, MIN_MT_CMAP_REPLACE] + cmap_menus.CLASSES + ops.CLASSES