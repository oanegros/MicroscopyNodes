import bpy

def axes_multiplexer_node_group():
    node_group = bpy.data.node_groups.get("multiplex_axes")
    if node_group:
        return node_group
    node_group= bpy.data.node_groups.new(type = 'GeometryNodeTree', name = "multiplex_axes")
    links = node_group.links
    interface = node_group.interface
    
    interface.new_socket("frontface culling (clip axes in front of data)", in_out="INPUT",socket_type='NodeSocketBool')
    interface.items_tree[-1].default_value = True
    interface.items_tree[-1].attribute_domain = 'POINT'
    for sideix, side in enumerate(['bottom', 'top']):
        for axix, ax in enumerate(['xy','yz','zx']):
            interface.new_socket(ax + " " + side, in_out="INPUT",socket_type='NodeSocketBool')
            interface.items_tree[-1].default_value = True
            interface.items_tree[-1].attribute_domain = 'POINT'
    group_input = node_group.nodes.new("NodeGroupInput")
    group_input.location = (-800,0)
    
    base = node_group.nodes.new("FunctionNodeInputInt")
    base.integer = 0
    base.location = (-800, 300)
    
    trav = node_group.nodes.new("ShaderNodeValue")
    trav.outputs[0].default_value = 0.1
    trav.location = (-800, 200)
    
    lastout = (base.outputs[0], trav.outputs[0])
    for ix, inputbool in enumerate(group_input.outputs[:-1]):
        mult = node_group.nodes.new("ShaderNodeMath")
        mult.operation = "MULTIPLY"
        mult.inputs[1].default_value = 10
        links.new(lastout[1], mult.inputs[0])
        
        add = node_group.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        links.new(lastout[0], add.inputs[0])
        links.new(mult.outputs[0], add.inputs[1])
        
        switch = node_group.nodes.new("GeometryNodeSwitch")
        switch.input_type = "INT"
        links.new(inputbool, switch.inputs[0])
        links.new(lastout[0], switch.inputs.get('False'))
        links.new(add.outputs[0], switch.inputs.get('True'))
        
        lastout = (switch.outputs[0], mult.outputs[0])
        
        for colix, node in enumerate([mult, add, switch]):
            node.location = (-600 + colix * 200 + ix *200, ix *-200 +500)
        
    interface.new_socket("multi-selection", in_out="OUTPUT",socket_type='NodeSocketInt')
    interface.items_tree[0].attribute_domain = 'POINT'
    group_output = node_group.nodes.new("NodeGroupOutput")
    
    group_output.location = (-300 + colix * 200 + ix *200, ix *-200 +500)
    links.new(lastout[0], group_output.inputs[0])
    return node_group


def axes_demultiplexer_node_group():
    node_group = bpy.data.node_groups.get("demultiplex_axes")
    if node_group:
        return node_group
    node_group= bpy.data.node_groups.new(type = 'GeometryNodeTree', name = "demultiplex_axes")
    links = node_group.links
    interface = node_group.interface
    
    interface.new_socket("multi-selection", in_out="INPUT",socket_type='NodeSocketInt')
    interface.items_tree[0].attribute_domain = 'POINT'
    group_input = node_group.nodes.new("NodeGroupInput")
    group_input.location = (-800,0)
    
    interface.new_socket("frontface culling (clip axes in front of data)", in_out="OUTPUT",socket_type='NodeSocketBool')
    interface.items_tree[-1].attribute_domain = 'POINT'
    for sideix, side in enumerate(['bottom', 'top']):
        for axix, ax in enumerate(['xy','yz','zx']):
            interface.new_socket(ax + " " + side, in_out="OUTPUT",socket_type='NodeSocketBool')
            interface.items_tree[-1].attribute_domain = 'POINT'
    group_output = node_group.nodes.new("NodeGroupOutput")
    group_output.location = (1200, 0)
    
    for ix, outputbool in enumerate(group_output.inputs[:-1]):
        div = node_group.nodes.new("ShaderNodeMath")
        div.operation = "DIVIDE"
        links.new(group_input.outputs[0], div.inputs[0])
        div.inputs[1].default_value = 10 ** ix
        
        trunc = node_group.nodes.new("ShaderNodeMath")
        trunc.operation = "TRUNC"
        links.new(div.outputs[0], trunc.inputs[0])

        mod = node_group.nodes.new("ShaderNodeMath")
        mod.operation = "MODULO"
        mod.inputs[1].default_value = 10
        links.new(trunc.outputs[0], mod.inputs[0])
        
        links.new(mod.outputs[0], outputbool)
        
        for colix, node in enumerate([div, trunc, mod]):
            node.location = (-600 + colix * 200 + ix *200, ix *200 -500)
    return node_group