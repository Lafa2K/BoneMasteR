import bpy

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

classes = (OBJECT_OT_AddBonesAtPivots,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
