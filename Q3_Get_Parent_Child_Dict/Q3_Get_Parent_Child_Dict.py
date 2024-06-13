import bpy

root = bpy.context.object
parent_child_dict = {}

def recurse(parent):
    if parent.children:
        children = parent.children
        parent_child_dict[parent.name] = [o.name for o in children]
        for ob in children:
            if ob.children:
                recurse(ob)
    return parent_child_dict

print(recurse(root)) 


        
            