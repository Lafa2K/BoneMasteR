import bpy

def AddBonesToEdges(self, context):
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

    for obj in selected_objects:
        if obj.type == 'MESH':
            amt = bpy.data.armatures.new(f"{obj.name}_armature")
            rig = bpy.data.objects.new(f"{obj.name}_armature_Object", amt)
            bpy.context.collection.objects.link(rig)

            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')

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

            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, f"Created bones for edges in {obj.name}")

    return {'FINISHED'}

class OBJECT_OT_AddBonesToEdges(bpy.types.Operator):
    bl_idname = "object.add_bones_to_edges"
    bl_label = "Add Bone to Edge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return AddBonesToEdges(self, context)

# Função para adicionar ossos no pivô com grupos de vértices
def AddBonesAtPivotsWithRootAndVertexGroups(self, context, bone_size):
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

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

    bone_size: bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )

    def execute(self, context):
        return AddBonesAtPivotsWithRootAndVertexGroups(self, context, self.bone_size)

classes = (
    OBJECT_OT_AddBonesAtPivots,
    OBJECT_OT_AddBonesToEdges,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bone_master_size = bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )

def unregister():
    del bpy.types.Scene.bone_master_size
    for cls in classes:
        bpy.utils.unregister_class(cls)
