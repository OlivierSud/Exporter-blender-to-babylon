"""
Utility module to disconnect and reconnect shader nodes from Material Output.
This prevents textures from being exported while preserving material colors/values.
"""
import bpy

# Global dictionary to store connections
_stored_connections = {}

def disconnect_all_shaders():
    """
    Disconnect all shaders from Material Output nodes in all materials.
    Stores the connections for later reconnection.
    Returns the number of disconnected links.
    """
    global _stored_connections
    _stored_connections = {}
    
    disconnect_count = 0
    
    # For each material
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Find the Material Output node
        material_output = None
        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL':
                material_output = node
                break
        
        if not material_output:
            continue
        
        # Check if Material Output is connected
        input_surface = material_output.inputs.get('Surface')
        is_connected = input_surface and input_surface.is_linked
        
        if is_connected:
            # Get links before removing them
            links_to_remove = [link for link in links if link.to_node == material_output and link.to_socket.name == 'Surface']
            for link in links_to_remove:
                from_node = link.from_node.name
                from_socket = link.from_socket.name
                _stored_connections[mat.name] = (from_node, from_socket)
                links.remove(link)
                disconnect_count += 1
    
    return disconnect_count

def reconnect_all_shaders():
    """
    Reconnect all previously disconnected shaders to Material Output nodes.
    Returns the number of reconnected links.
    """
    global _stored_connections
    
    reconnect_count = 0
    
    # For each material
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Find the Material Output node
        material_output = None
        for node in nodes:
            if node.type == 'OUTPUT_MATERIAL':
                material_output = node
                break
        
        if not material_output:
            continue
        
        to_socket = material_output.inputs.get('Surface')
        if not to_socket:
            continue
        
        # First, use stored connection if it exists
        if mat.name in _stored_connections:
            from_node_name, from_socket_name = _stored_connections[mat.name]
            from_node = nodes.get(from_node_name)
            
            if from_node:
                from_socket = from_node.outputs.get(from_socket_name)
                if from_socket:
                    links.new(from_socket, to_socket)
                    reconnect_count += 1
                    del _stored_connections[mat.name]
                    continue
        
        # If no stored connection, find the first connected shader
        shader_node = None
        for node in nodes:
            if node.type in ('ShaderNodeBsdfPrincipled', 'ShaderNodeBsdfDiffuse', 'ShaderNodeBsdfGlossy', 
                            'ShaderNodeBsdfTransparent', 'ShaderNodeBsdfRefraction', 'ShaderNodeBsdfAnisotropic',
                            'ShaderNodeBsdfVelvet', 'ShaderNodeBsdfToon', 'ShaderNodeSubsurfaceScattering',
                            'ShaderNodeMixShader', 'ShaderNodeAddShader', 'ShaderNodeEmission'):
                shader_node = node
                break
        
        # If no shader found by type, search for any node with a SHADER output socket
        if not shader_node:
            for node in nodes:
                for output in node.outputs:
                    if output.type == 'SHADER':
                        shader_node = node
                        break
                if shader_node:
                    break
        
        # Connect the found shader to Material Output Surface
        if shader_node:
            # Find the first SHADER socket in outputs
            for socket in shader_node.outputs:
                if socket.type == 'SHADER':
                    links.new(socket, to_socket)
                    reconnect_count += 1
                    break
    
    return reconnect_count
