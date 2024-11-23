import bpy

def AddBonesToEdges(self, context):
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

    bone_size = context.scene.bone_master_size

    for obj in selected_objects:
        if obj.type == 'MESH':
            amt = bpy.data.armatures.new(f"{obj.name}_armature")
            rig = bpy.data.objects.new(f"{obj.name}_armature_Object", amt)
            bpy.context.collection.objects.link(rig)

            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')

            parent_bone = amt.edit_bones.new("ROOT")
            parent_bone.head = (0, 0, 0)
            parent_bone.tail = (0, 0, bone_size)

            selected_edges = [e for e in obj.data.edges if e.select]

            if not selected_edges:
                self.report({'WARNING'}, f"No edges selected for {obj.name}")
                continue

            for idx, edge in enumerate(selected_edges):
                v1 = obj.data.vertices[edge.vertices[0]].co
                v2 = obj.data.vertices[edge.vertices[1]].co

                v1_world = obj.matrix_world @ v1
                v2_world = obj.matrix_world @ v2

                bone_name = f"Bone_{obj.name}_Edge_{idx+1}"
                bone = amt.edit_bones.new(bone_name)
                bone.head = v1_world
                bone.tail = v2_world

                bone.parent = parent_bone
                bone.use_connect = False

                edge_length = (v2_world - v1_world).length
                bone.tail = bone.head + (v2_world - v1_world).normalized() * edge_length

            self.report({'INFO'}, f"Created bones for edges in {obj.name}")

    return {'FINISHED'}


class OBJECT_OT_AddBonesToEdges(bpy.types.Operator):
    bl_idname = "object.add_bones_to_edges"
    bl_label = "Add Bone to Edge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return AddBonesToEdges(self, context)


def AddBonesAtPivotsWithRootAndVertexGroups(self, context):
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

    bone_size = context.scene.bone_master_size

    amt = bpy.data.armatures.new("Armature_with_bones")
    rig = bpy.data.objects.new("Armature_with_bones_Object", amt)
    bpy.context.collection.objects.link(rig)
    
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    
    root_bone = amt.edit_bones.new("ROOT")
    root_bone.head = (0, 0, 0)
    root_bone.tail = (0, 0, bone_size)
    
    for obj in selected_objects:
        if obj.type == 'MESH':
            pivot_position = obj.location
            
            bone = amt.edit_bones.new(obj.name + "_bone")
            bone.head = pivot_position
            bone.tail = (pivot_position[0], pivot_position[1], pivot_position[2] + bone_size)
            bone.parent = root_bone
            bone.use_connect = False
            
            if obj.vertex_groups.get(obj.name + "_bone") is None:
                obj.vertex_groups.new(name=obj.name + "_bone")
            
            vgroup = obj.vertex_groups[obj.name + "_bone"]
            for vert in obj.data.vertices:
                vgroup.add([vert.index], 1.0, 'REPLACE')

    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.context.view_layer.objects.active = rig
    self.report({'INFO'}, f"{len(selected_objects)} Done: Bones ROOT and Vertex Groups!")

    return {'FINISHED'}


class OBJECT_OT_AddBonesAtPivots(bpy.types.Operator):
    bl_idname = "object.add_bones_at_pivots"
    bl_label = "Add bones to object Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bone_size = context.scene.bone_master_size
        return AddBonesAtPivotsWithRootAndVertexGroups(self, context)


import bpy
import mathutils

class OBJECT_OT_AddBonesToVertices(bpy.types.Operator):
    bl_idname = "object.add_bones_to_vertices"
    bl_label = "Add Bone to Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        bone_size = context.scene.bone_master_size
        bone_to_vertex_normal = context.scene.bone_to_vertex_normal

        for obj in selected_objects:
            if obj.type == 'MESH':
                amt = bpy.data.armatures.new(f"{obj.name}_armature")
                rig = bpy.data.objects.new(f"{obj.name}_armature_Object", amt)
                bpy.context.collection.objects.link(rig)

                bpy.ops.object.mode_set(mode='OBJECT')

                bpy.context.view_layer.objects.active = rig
                bpy.ops.object.mode_set(mode='EDIT')

                parent_bone = amt.edit_bones.new("ROOT")
                parent_bone.head = (0, 0, 0)
                parent_bone.tail = (0, 0, bone_size)

                selected_vertices = [v for v in obj.data.vertices if v.select]

                if not selected_vertices:
                    self.report({'WARNING'}, f"No vertices selected for {obj.name}")
                    continue

                for idx, vertex in enumerate(selected_vertices):
                    vertex_position = obj.matrix_world @ vertex.co

                    bone_name = f"Bone_{obj.name}_Vertex_{idx+1}"
                    bone = amt.edit_bones.new(bone_name)

                    bone.head = vertex_position

                    if bone_to_vertex_normal:
                        normal = obj.data.vertices[vertex.index].normal
                        normal_world = obj.matrix_world.to_3x3() @ normal  # Transformar a normal para o espaço global

                        bone.tail = bone.head + normal_world * bone_size  # Coloca o tail na direção da normal

                    else:
                        bone.tail = (vertex_position[0], vertex_position[1], vertex_position[2] + bone_size)

                    bone.parent = parent_bone
                    bone.use_connect = False

                self.report({'INFO'}, f"Created bones for selected vertices in {obj.name}")

        return {'FINISHED'}



# Função de registro
def register():
    if not hasattr(bpy.types, "OBJECT_OT_AddBonesAtPivots"):
        bpy.utils.register_class(OBJECT_OT_AddBonesAtPivots)

    if not hasattr(bpy.types, "OBJECT_OT_AddBonesToEdges"):
        bpy.utils.register_class(OBJECT_OT_AddBonesToEdges)

    if not hasattr(bpy.types, "OBJECT_OT_AddBonesToVertices"):
        bpy.utils.register_class(OBJECT_OT_AddBonesToVertices)

    bpy.types.Scene.bone_master_size = bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )


def unregister():
    if hasattr(bpy.types, "OBJECT_OT_AddBonesAtPivots"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesAtPivots)

    if hasattr(bpy.types, "OBJECT_OT_AddBonesToEdges"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesToEdges)

    if hasattr(bpy.types, "OBJECT_OT_AddBonesToVertices"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesToVertices)

    del bpy.types.Scene.bone_master_size
