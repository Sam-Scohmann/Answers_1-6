bl_info = {
    "name": "3_Point_Lighter",
    "author": "Suvigya_Mishra",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "Generates a 3-point lighting setup.",
    "category": "Lighting",
}

import bpy
import random
import mathutils

class ThreePointLighterProperties(bpy.types.PropertyGroup):
    light1_type: bpy.props.EnumProperty(
        name="Light Type",
        description="Choose the type of the first light",
        items=[
            ('POINT', "Point", ""),
            ('SUN', "Sun", ""),
            ('SPOT', "Spot", ""),
            ('AREA', "Area", ""),
        ],
        default='AREA',
    )
    light1_color: bpy.props.FloatVectorProperty(
        name="Light 1 Color",
        description="Choose the color of the first light",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )
    light2_type: bpy.props.EnumProperty(
        name="Light Type",
        description="Choose the type of the second light",
        items=[
            ('POINT', "Point", ""),
            ('SUN', "Sun", ""),
            ('SPOT', "Spot", ""),
            ('AREA', "Area", ""),
        ],
        default='AREA',
    )
    light2_color: bpy.props.FloatVectorProperty(
        name="Light 2 Color",
        description="Choose the color of the second light",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )
    light3_type: bpy.props.EnumProperty(
        name="Light Type",
        description="Choose the type of the third light",
        items=[
            ('POINT', "Point", ""),
            ('SUN', "Sun", ""),
            ('SPOT', "Spot", ""),
            ('AREA', "Area", ""),
        ],
        default='AREA',
    )
    light3_color: bpy.props.FloatVectorProperty(
        name="Light 3 Color",
        description="Choose the color of the third light",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0),
    )

class OBJECT_PT_ThreePointLighterPanel(bpy.types.Panel):
    bl_label = "3 Point Lighter"
    bl_idname = "OBJECT_PT_ThreePointLighterPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3 Point Lighter'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        three_point_lighter = scene.three_point_lighter

        # Instruction Panel
        box = layout.box()
        box.label(text="Instruction")
        col = box.column(align=True)
        col.label(text="Step1: Select any parent object(mesh or empty) or individual mesh.")
        col.label(text="Step2: 'Visualize Bounds' > 'Generate Lights'.")

        # Generate 3 point lights Panel
        box = layout.box()
        box.label(text="Generate 3 point lights")
        col = box.column(align=True)
        col.operator("lighting.visualize_bounds", text="Visualize Bounds")
        col.operator("lighting.generate_lights", text="Generate Lights")

        # Update Lights Panel
        box = layout.box()
        box.label(text="Update Lights")
        col = box.column(align=True)

        row = col.row(align=True)
        row.label(text="MyLight_1")
        row.prop(three_point_lighter, "light1_type", text="")
        row.prop(three_point_lighter, "light1_color", text="")

        row = col.row(align=True)
        row.label(text="MyLight_2")
        row.prop(three_point_lighter, "light2_type", text="")
        row.prop(three_point_lighter, "light2_color", text="")

        row = col.row(align=True)
        row.label(text="MyLight_3")
        row.prop(three_point_lighter, "light3_type", text="")
        row.prop(three_point_lighter, "light3_color", text="")

        row = col.row(align=True)
        row.operator("lighting.update_lights", text="Update")
        row.operator("lighting.remove_lights", text="Remove Lights")

class LIGHTING_OT_VisualizeBounds(bpy.types.Operator):
    bl_idname = "lighting.visualize_bounds"
    bl_label = "Visualize Bounds"
    bl_description = "Visualize the bounds of the selected object"

    def execute(self, context):
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

        def create_bounding_box(vertices):
            if not vertices:
                print("No vertices provided.")
                return None

            # Calculate the min and max coordinates
            min_x = min(v[0] for v in vertices)
            max_x = max(v[0] for v in vertices)
            min_y = min(v[1] for v in vertices)
            max_y = max(v[1] for v in vertices)
            min_z = min(v[2] for v in vertices)
            max_z = max(v[2] for v in vertices)

            # Calculate the spans
            x_span = max_x - min_x
            y_span = max_y - min_y
            z_span = max_z - min_z

            # Create a cube
            bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
            cube = bpy.context.object
            
            # Scale the cube
            cube.scale = (x_span / 2, y_span / 2, z_span / 2)
            
            # Apply the scale to the cube
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            # Move the origin to the base of the cube
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.translate(value=(0, 0, z_span / 2))
            bpy.ops.object.editmode_toggle()
            
            # Move the cube to the specified min bounds
            cube.location = (min_x + x_span / 2, min_y + y_span / 2, min_z)
            cube.hide_render = True
            cube.display_type = 'WIRE'
            # Return the cube object
            return cube

        def create_bounding_boxes():
            parent_ob = bpy.context.object
            vertices = get_all_world_mesh_verts(parent_ob)
            cube = create_bounding_box(vertices)
            cube2 = create_bounding_box(vertices)
            cube2.scale[0]*=3
            cube2.scale[1]*=3
            cube2.scale[2]*=1.2 
            cube.name = "BoundingBoxCube"
            cube2.name = "LightDomain"

        def delete_boxes():
            boxes = ["BoundingBoxCube", "LightDomain"]
            all_object_names = [o.name for o in bpy.data.objects]

            for ob_name in boxes:
                if ob_name in all_object_names:
                    ob = bpy.data.objects[ob_name]
                    if ob.type == 'MESH':
                        bpy.data.meshes.remove(ob.data)
        delete_boxes()
        create_bounding_boxes()
        self.report({'INFO'}, "Visualize Bounds executed")
        return {'FINISHED'}

class LIGHTING_OT_GenerateLights(bpy.types.Operator):
    bl_idname = "lighting.generate_lights"
    bl_label = "Generate Lights"
    bl_description = "Generate 3 point lights"

    def execute(self, context):
        def get_bounding_box_dimensions(obj):
            local_coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
            min_x = min(v.x for v in local_coords)
            max_x = max(v.x for v in local_coords)
            min_y = min(v.y for v in local_coords)
            max_y = max(v.y for v in local_coords)
            min_z = min(v.z for v in local_coords)
            max_z = max(v.z for v in local_coords)
            
            return min_x, max_x, min_y, max_y, min_z, max_z

        def generate_random_point_within_bounds(min_x, max_x, min_y, max_y, z_range, error=0.1):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            z = random.uniform(z_range[0], z_range[1])
            return (x, y, z)

        def spawn_point(location, name):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=location)
            sphere = bpy.context.object
            sphere.name = name
            sphere.hide_render = True
            sphere.display_type = 'WIRE'
            
        def generate_random_surface_point(min_x, max_x, min_y, max_y, z_range, surface='z'):
            if surface == 'z':
                x = random.uniform(min_x, max_x)
                y = random.uniform(min_y, max_y)
                z = random.choice([z_range[0], z_range[1]])
            elif surface == 'x':
                x = random.choice([min_x, max_x])
                y = random.uniform(min_y, max_y)
                z = random.uniform(z_range[0], z_range[1])
            elif surface == 'y':
                x = random.uniform(min_x, max_x)
                y = random.choice([min_y, max_y])
                z = random.uniform(z_range[0], z_range[1])
            return (x, y, z)

        def spawn_inner_points(box_name):
            # Get active camera
            camera = bpy.context.scene.camera
            if camera is None:
                print("No active camera found.")
                return
            
            # Get the bounding box object
            bounding_box = bpy.data.objects[box_name]
            if bounding_box is None or bounding_box.type != 'MESH':
                print("No active bounding box mesh object found.")
                return

            # Get bounding box dimensions
            min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box_dimensions(bounding_box)
            z_span = max_z - min_z

            # Point 1: Closest to the camera, 70% to 100% of the z-height
            z_range1 = (min_z + 0.7 * z_span, max_z)
            point_1 = generate_random_point_within_bounds(min_x, max_x, min_y, max_y, z_range1)
            spawn_point(point_1, "Point_1")

            # Point 2: Farthest from the camera, 60% to 80% of the z-height
            z_range2 = (min_z + 0.6 * z_span, min_z + 0.8 * z_span)
            point_2 = generate_random_point_within_bounds(min_x, max_x, min_y, max_y, z_range2)
            spawn_point(point_2, "Point_2")

            # Point 3: Right side of the box w.r.t the camera, 40% to 60% of the z-height
            if camera.location.x > (min_x + max_x) / 2:
                # Camera is to the left, place point on the right
                x_range3 = (min_x + 0.5 * (max_x - min_x), max_x)
            else:
                # Camera is to the right, place point on the left
                x_range3 = (min_x, min_x + 0.5 * (max_x - min_x))
            z_range3 = (min_z + 0.4 * z_span, min_z + 0.6 * z_span)
            point_3 = generate_random_point_within_bounds(x_range3[0], x_range3[1], min_y, max_y, z_range3)
            spawn_point(point_3, "Point_3")

        def spawn_outer_points(box_name):
            # Get active camera
            camera = bpy.context.scene.camera
            if camera is None:
                print("No active camera found.")
                return
            
            # Get the bounding box object
            bounding_box = bpy.data.objects[box_name]
            if bounding_box is None or bounding_box.type != 'MESH':
                print("No active bounding box mesh object found.")
                return

            # Get bounding box dimensions
            min_x, max_x, min_y, max_y, min_z, max_z = get_bounding_box_dimensions(bounding_box)
            z_span = max_z - min_z

            # Point2_1: Closest to the camera, 70% to 100% of the z-height
            z_range1 = (min_z + 0.7 * z_span, max_z)
            point2_1 = generate_random_surface_point(min_x, max_x, min_y, max_y, z_range1, surface='z')
            spawn_point(point2_1, "Point2_1")

            # Point2_2: Farthest from the camera, 60% to 80% of the z-height
            z_range2 = (min_z + 0.6 * z_span, min_z + 0.8 * z_span)
            point2_2 = generate_random_surface_point(min_x, max_x, min_y, max_y, z_range2, surface='z')
            spawn_point(point2_2, "Point2_2")

            # Point2_3: Right side of the box w.r.t the camera, 40% to 60% of the z-height
            if camera.location.x > (min_x + max_x) / 2:
                # Camera is to the left, place point on the right surface
                point2_3 = generate_random_surface_point(min_x, max_x, min_y, max_y, (min_z + 0.4 * z_span, min_z + 0.6 * z_span), surface='x')
            else:
                # Camera is to the right, place point on the left surface
                point2_3 = generate_random_surface_point(min_x, max_x, min_y, max_y, (min_z + 0.4 * z_span, min_z + 0.6 * z_span), surface='x')
            spawn_point(point2_3, "Point2_3")



        def create_light_at_point(location, target_name, light_name):
            # Add an area light at the specified location
            bpy.ops.object.light_add(type='AREA', location=location)
            light = bpy.context.object
            light.name = light_name
            light.data.energy = 1000
            light.data.size = 1.0
            light.show_name = True

            # Get the target object
            target = bpy.data.objects.get(target_name)
            if target is None:
                print(f"Target object {target_name} not found.")
                return

            # Point the light towards the target
            direction = mathutils.Vector(target.location) - mathutils.Vector(location)
            rot_quat = direction.to_track_quat('-Z', 'Y')
            light.rotation_euler = rot_quat.to_euler()
            
            return light

        def create_lights():
            # Define the point and light names
            point_names = ["Point2_1", "Point2_2", "Point2_3"]
            target_names = ["Point_1", "Point_2", "Point_3"]
            light_names = ["MyLight_1", "MyLight_2", "MyLight_3"]

            for point_name, target_name, light_name in zip(point_names, target_names, light_names):
                # Get the point object
                point = bpy.data.objects.get(point_name)
                if point is None:
                    print(f"Point object {point_name} not found.")
                    continue

                # Create light at the point location facing the target
                create_light_at_point(point.location, target_name, light_name)


        def delete_points():
            point_names = ["Point2_1", "Point2_2", "Point2_3"]
            target_names = ["Point_1", "Point_2", "Point_3"]
            my_object_names = point_names + target_names 
            all_object_names = [o.name for o in bpy.data.objects]

            for ob_name in my_object_names:
                if ob_name in all_object_names:
                    ob = bpy.data.objects[ob_name]
                    if ob.type == 'MESH':
                        bpy.data.meshes.remove(ob.data)
                        
        def delete_lights():
            light_names = ["MyLight_1", "MyLight_2", "MyLight_3"]
            all_object_names = [o.name for o in bpy.data.objects]
            for ob_name in light_names:
                if ob_name in all_object_names:
                    ob = bpy.data.objects[ob_name]
                    if ob.type == 'LIGHT':
                        bpy.data.lights.remove(ob.data)
                    
        delete_lights()
        spawn_inner_points("BoundingBoxCube")
        spawn_outer_points("LightDomain")
        create_lights()
        delete_points()
        self.report({'INFO'}, "Generate Lights executed")
        return {'FINISHED'}

class LIGHTING_OT_UpdateLights(bpy.types.Operator):
    bl_idname = "lighting.update_lights"
    bl_label = "Update Lights"
    bl_description = "Update the lights"

    def execute(self, context):
        scene = bpy.context.scene
        light_names = ["MyLight_1", "MyLight_2", "MyLight_3"]
        all_object_names = [o.name for o in bpy.data.objects]
        if 'MyLight_1' in all_object_names:
            light_1 = bpy.data.objects['MyLight_1']
            light_1.data.type = scene.three_point_lighter.light1_type
            light_1.data.color = scene.three_point_lighter.light1_color
        if 'MyLight_2' in all_object_names:
            light_2 = bpy.data.objects['MyLight_2']
            light_2.data.type = scene.three_point_lighter.light2_type
            light_2.data.color = scene.three_point_lighter.light2_color
        if 'MyLight_3' in all_object_names:
            light_3 = bpy.data.objects['MyLight_3']
            light_3.data.type = scene.three_point_lighter.light3_type
            light_3.data.color = scene.three_point_lighter.light3_color  
        self.report({'INFO'}, "Update Lights executed")
        return {'FINISHED'}

class LIGHTING_OT_RemoveLights(bpy.types.Operator):
    bl_idname = "lighting.remove_lights"
    bl_label = "Remove Lights"
    bl_description = "Remove the lights"

    def execute(self, context):
        boxes = ["BoundingBoxCube", "LightDomain"]
        point_names = ["Point2_1", "Point2_2", "Point2_3"]
        target_names = ["Point_1", "Point_2", "Point_3"]
        light_names = ["MyLight_1", "MyLight_2", "MyLight_3"]

        my_object_names = point_names + target_names + light_names + boxes
        all_object_names = [o.name for o in bpy.data.objects]

        for ob_name in my_object_names:
            if ob_name in all_object_names:
                ob = bpy.data.objects[ob_name]
                if ob.type == 'MESH':
                    bpy.data.meshes.remove(ob.data)
                elif ob.type == 'LIGHT':
                    bpy.data.lights.remove(ob.data)
                
        self.report({'INFO'}, "Remove Lights executed")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ThreePointLighterProperties)
    bpy.utils.register_class(OBJECT_PT_ThreePointLighterPanel)
    bpy.utils.register_class(LIGHTING_OT_VisualizeBounds)
    bpy.utils.register_class(LIGHTING_OT_GenerateLights)
    bpy.utils.register_class(LIGHTING_OT_UpdateLights)
    bpy.utils.register_class(LIGHTING_OT_RemoveLights)
    bpy.types.Scene.three_point_lighter = bpy.props.PointerProperty(type=ThreePointLighterProperties)

def unregister():
    bpy.utils.unregister_class(ThreePointLighterProperties)
    bpy.utils.unregister_class(OBJECT_PT_ThreePointLighterPanel)
    bpy.utils.unregister_class(LIGHTING_OT_VisualizeBounds)
    bpy.utils.unregister_class(LIGHTING_OT_GenerateLights)
    bpy.utils.unregister_class(LIGHTING_OT_UpdateLights)
    bpy.utils.unregister_class(LIGHTING_OT_RemoveLights)
    del bpy.types.Scene.three_point_lighter

if __name__ == "__main__":
    register()
