bl_info = {
    "name": "MultiExporter",
    "author": "Suvigya Mishra",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool",
    "description": "Exports selected objects in various formats.",
    "category": "Object",
}

import bpy
import os

class ExportObjectProperties(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty(name="Object Name")
    file_format: bpy.props.EnumProperty(
        name="File Format",
        description="Format to export the object to",
        items=[
            ('FBX', "FBX", ""),
            ('OBJ', "OBJ", ""),
            ('ALEMBIC', "ALEMBIC", ""),
            ('STL', "STL", ""),
            ('COLLADA', "COLLADA", "")
        ]
    )

class MultiExporterProperties(bpy.types.PropertyGroup):
    export_path: bpy.props.StringProperty(
        name="Export Path",
        description="Path to export the objects to",
        default="//",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    objects: bpy.props.CollectionProperty(type=ExportObjectProperties)

class OBJECT_OT_SelectObjects(bpy.types.Operator):
    bl_idname = "object.select_objects_to_export"
    bl_label = "Select Objects to Export"
    bl_description = "Select objects to export and create export info rows"

    def execute(self, context):
        scene = context.scene
        multi_exporter = scene.multi_exporter

        multi_exporter.objects.clear()

        for obj in bpy.context.selected_objects:
            item = multi_exporter.objects.add()
            item.object_name = obj.name
            item.file_format = 'FBX'  # Default value

        return {'FINISHED'}

class OBJECT_OT_ExportObjects(bpy.types.Operator):
    bl_idname = "object.export_objects"
    bl_label = "Export"
    bl_description = "Export the selected objects to the specified formats"

    def execute(self, context):
        scene = context.scene
        multi_exporter = scene.multi_exporter

        for obj in multi_exporter.objects:
            object_name = obj.object_name
            export_format = obj.file_format
            export_path = bpy.path.abspath(multi_exporter.export_path)
            file_path = os.path.join(export_path, f"{object_name}.{export_format.lower()}")

            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[object_name].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[object_name]

            if export_format == 'FBX':
                bpy.ops.export_scene.fbx(filepath=file_path, use_selection=True)
            elif export_format == 'OBJ':
                bpy.ops.wm.obj_export(filepath=file_path, export_selected_objects=True)
            elif export_format == 'ALEMBIC':
                bpy.ops.wm.alembic_export(filepath=file_path, selected=True)
            elif export_format == 'STL':
                bpy.ops.export_mesh.stl(filepath=file_path, use_selection=True)
            elif export_format == 'COLLADA':
                bpy.ops.wm.collada_export(filepath=file_path, selected=True)

        self.report({'INFO'}, "Objects exported successfully")
        return {'FINISHED'}

class OBJECT_PT_MultiExporterPanel(bpy.types.Panel):
    bl_label = "MultiExporter"
    bl_idname = "OBJECT_PT_MultiExporterPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MultiExporter'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        multi_exporter = scene.multi_exporter

        layout.operator("object.select_objects_to_export", text="Select Objects to Export")

        if multi_exporter.objects:
            box = layout.box()
            box.label(text=f"Object Export Info (N={len(multi_exporter.objects)})")
            
            for obj in multi_exporter.objects:
                row = box.row()
                row.prop_search(obj, "object_name", bpy.data, "objects", text="Object Picker")
                row.prop(obj, "file_format", text="File Format", expand=True)

            layout.prop(multi_exporter, "export_path")
            layout.operator("object.export_objects", text="Export")

def register():
    bpy.utils.register_class(ExportObjectProperties)
    bpy.utils.register_class(MultiExporterProperties)
    bpy.utils.register_class(OBJECT_OT_SelectObjects)
    bpy.utils.register_class(OBJECT_OT_ExportObjects)
    bpy.utils.register_class(OBJECT_PT_MultiExporterPanel)
    bpy.types.Scene.multi_exporter = bpy.props.PointerProperty(type=MultiExporterProperties)

def unregister():
    bpy.utils.unregister_class(ExportObjectProperties)
    bpy.utils.unregister_class(MultiExporterProperties)
    bpy.utils.unregister_class(OBJECT_OT_SelectObjects)
    bpy.utils.unregister_class(OBJECT_OT_ExportObjects)
    bpy.utils.unregister_class(OBJECT_PT_MultiExporterPanel)
    del bpy.types.Scene.multi_exporter

if __name__ == "__main__":
    register()
