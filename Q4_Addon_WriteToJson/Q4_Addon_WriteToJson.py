bl_info = {
    "name": "json_object_info",
    "author": "Suvigya Mishra",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "Writes selected object info to a JSON file.",
    "category": "Object",
}

import bpy
import json
import os
import math

class JsonObjectInfoProperties(bpy.types.PropertyGroup):
    file_name: bpy.props.StringProperty(
        name="File Name",
        description="Name of the JSON file to write object info to",
        default="json_filename",
        maxlen=1024,
    )

class OBJECT_OT_WriteJson(bpy.types.Operator):
    bl_idname = "object.write_json"
    bl_label = "Write Json"
    bl_description = "Write selected object info to a JSON file"

    def execute(self, context):
        
        json_file_name = bpy.context.scene.json_object_info.file_name

        selected_objects = bpy.context.selected_objects
        blend_filepath = bpy.data.filepath
        blend_name = blend_filepath.split('\\')[-1]
        path =   blend_filepath.split(blend_name)[0]
        json_data = []
        with open(path+json_file_name+".json","w") as outfile:
            for ob in selected_objects:
                dictionary = {
                    "object_name" : ob.name,
                    "location" : (ob.location[0], ob.location[1], ob.location[2]),
                    "rotation" : (math.degrees(ob.rotation_euler[0]) , math.degrees(ob.rotation_euler[1]) , math.degrees(ob.rotation_euler[2])),
                    "scale" : (ob.scale[0], ob.scale[0], ob.scale[0]),
                    "parent" : ob.parent.name if ob.parent else None,
                    "children" : [ch.name for ch in ob.children]
                }
                json_data.append(dictionary)
            json_object = json.dumps(json_data, indent = 4)
            outfile.write(json_object)

        self.report({'INFO'}, f"Object info written to {path}")
        return {'FINISHED'}

class OBJECT_PT_JsonObjectInfoPanel(bpy.types.Panel):
    bl_label = "Write object info to json"
    bl_idname = "OBJECT_PT_JsonObjectInfoPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'json_object_info'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.json_object_info

        layout.prop(props, "file_name")
        layout.operator("object.write_json", text="Write Json")

def register():
    bpy.utils.register_class(JsonObjectInfoProperties)
    bpy.utils.register_class(OBJECT_OT_WriteJson)
    bpy.utils.register_class(OBJECT_PT_JsonObjectInfoPanel)
    bpy.types.Scene.json_object_info = bpy.props.PointerProperty(type=JsonObjectInfoProperties)

def unregister():
    bpy.utils.unregister_class(JsonObjectInfoProperties)
    bpy.utils.unregister_class(OBJECT_OT_WriteJson)
    bpy.utils.unregister_class(OBJECT_PT_JsonObjectInfoPanel)
    del bpy.types.Scene.json_object_info

if __name__ == "__main__":
    register()
