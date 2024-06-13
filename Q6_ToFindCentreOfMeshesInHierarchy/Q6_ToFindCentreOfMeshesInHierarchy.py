import bpy
import mathutils

def get_world_mesh_verts(ob):         
    if ob.type == 'MESH':
        world_matrix = ob.matrix_world
        return [world_matrix @ vertex.co for vertex in ob.data.vertices]
    else:
        return []
    

def get_all_world_mesh_verts(parent_ob):
    verts = []
    if parent_ob.type == 'MESH':
        verts.extend(get_world_mesh_verts(parent_ob))
    for child in parent_ob.children_recursive:
        if child.type == 'MESH':
            verts.extend(get_world_mesh_verts(child))                            
    return verts



def calc_center_of_meshes(obj):
    verts = get_all_world_mesh_verts(obj)    
    if not verts:
        return None
    
    center = mathutils.Vector((0, 0, 0))
    
    for vert in verts:
        center += vert
    
    center /= len(verts)
    return center



parent_obj = bpy.context.object

if parent_obj:
    center = calc_center_of_meshes(parent_obj)
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=center, scale=(1, 1, 1))
    if center:
        print(f"Center of meshes: {center}")
    else:
        print("No mesh children found.")
else:
    print("No object selected.")
