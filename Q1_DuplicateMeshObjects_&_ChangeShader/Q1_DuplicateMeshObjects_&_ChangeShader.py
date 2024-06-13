import bpy, os
import numpy as np

#inputs
object_name_override = "ImagineObject" #leave it empty as "" if override not desired
collection_override = "ImagineCollection"
gap_between_objects = 0.3  #ratio between 0 -1

#Get Object, Mesh data 
ob = bpy.context.object
mesh = ob.data

#get/create Collection
if collection_override == "":
    collection = bpy.context.collection #or bpy.data.collections['Collection_name']
else:
    if collection_override not in [c.name for c in bpy.data.collections]:
        bpy.data.collections.new(collection_override)
        collection = bpy.data.collections[collection_override]
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections[collection_override]    
#get object bounding values in X and Y
mesh_x_vals = []
mesh_y_vals = []
for v in mesh.vertices:
    x_val = v.co[0]
    y_val = v.co[1]
    mesh_x_vals.append(x_val)    
    mesh_y_vals.append(y_val)
    
min_x = min(mesh_x_vals)
max_x = max(mesh_x_vals)   
min_y = min(mesh_y_vals)
max_y = max(mesh_y_vals)  

x_span = max_x - min_x
y_span = max_y - min_y
#print(x_span, y_span)

#get object scale, rotation
scale = ob.scale
rot = ob.rotation_euler

#Delete objects and material from collection
if collection is not None:
    for o in collection.objects:
        if len(o.material_slots) > 0:
            m = o.material_slots[0].material
            bpy.data.materials.remove(m)
        if o.type == 'MESH':
            bpy.data.meshes.remove(o.data)
        #bpy.data.objects.remove(o)

#Create Objects and link it into the Scene
for i in range(-2,2):
    for j in range(-2,2):
        if object_name_override == "":
            new_ob_name = ob.name + "_" +str(i+2)+str(j+2)
        else:
            new_ob_name = object_name_override + "_" +str(i+2)+str(j+2)
        bpy.data.objects.new(name = new_ob_name, object_data = mesh.copy())
        new_ob = bpy.data.objects[new_ob_name]
        collection.objects.link(new_ob)
        
        x_location = x_span * ( j *(1 + gap_between_objects) + 1) *scale[0]
        y_location = y_span * ( i *(1 + gap_between_objects) + 1) *scale[1]
        new_ob.location = (x_location,y_location,0) 
        new_ob.scale = scale
        new_ob.rotation_euler = rot
        

"""Get Textures from Path"""
rel_texture_path = 'SuzaneTextures//'
file_path = bpy.data.filepath
dirname = os.path.dirname(file_path)
tex_dir = os.path.join(dirname, rel_texture_path)
textures = [f for f in os.listdir(tex_dir) if f.endswith('.png')]

"""Load textures"""
for tex in textures:
    tex_path = os.path.join(tex_dir, tex)
    bpy.data.images.load(tex_path, check_existing=True)

"""For each object in collection"""    
for ob in collection.objects:
    """Choose mat"""
    tex_choice = np.random.choice(textures)
    mat_name = tex_choice.split('.png')[0]
    
    """Create mat"""
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True

    """NODE CREATION"""
    bsdf = mat.node_tree.nodes['Principled BSDF']

    fresnel = mat.node_tree.nodes.new("ShaderNodeFresnel")
    fresnel.location = (-200,2)

    hsv = mat.node_tree.nodes.new("ShaderNodeHueSaturation")
    hsv.location = (-200, 300)

    img_tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    img_tex.location = (-500, 250)

    """NODE LINKS"""
    mat.node_tree.links.new(bsdf.inputs[0], hsv.outputs[0])
    mat.node_tree.links.new(bsdf.inputs[26], hsv.outputs[0])
    mat.node_tree.links.new(bsdf.inputs[27], fresnel.outputs[0])
    mat.node_tree.links.new(hsv.inputs[4], img_tex.outputs[0])

    """SET VALUES"""
    img_tex.image = bpy.data.images[tex_choice]
    hsv.inputs[0].default_value = np.random.random()
    
    """APPLY MATERIAL"""
    if len(ob.material_slots)==0:
        ob.data.materials.append(mat)
    else:
        ob.material_slots[0].material = mat
        
    """rename Mat"""
    mat.name = mat.name.split('.')[0] + "_" +ob.name.split('_')[1]
    
    
    

"""COPY MODIFIERS FROM ACTIVE TO DUPLICATES"""
active_obj = bpy.context.view_layer.objects.active

# Get duplicvate objects except the active object
duplicate_objects = [o for o in collection.objects if o != active_obj]

# Loop through all modifiers of the active object
for mod in active_obj.modifiers:
    for obj in duplicate_objects:
        new_mod = obj.modifiers.new(name=mod.name, type=mod.type)
        # Copy properties from the source modifier to the new modifier
        for attr in dir(mod):
            if not attr.startswith("_") and hasattr(new_mod, attr):
                try:
                    setattr(new_mod, attr, getattr(mod, attr))
                except AttributeError:
                    pass
        
        print(f"Copied modifier '{mod.name}' of type '{mod.type}' from {active_obj.name} to {obj.name}")


