import bpy

class VIEW3D_PT_BonesMasterPanel(bpy.types.Panel):
    bl_label = "Bone Master"
    bl_idname = "VIEW3D_PT_bone_master_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoneMaster'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "bone_master_size", text="Bone Size")
        
        layout.operator("object.add_bones_at_pivots", text="Add bones to object Origin")
        layout.operator("object.add_bones_to_edges", text="Add Bone to Edge")

        layout.operator("object.add_bones_to_vertices", text="Add Bone to Vertex")

classes = (VIEW3D_PT_BonesMasterPanel,)


def register():
    bpy.types.Scene.bone_master_size = bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    del bpy.types.Scene.bone_master_size
    for cls in classes:
        bpy.utils.unregister_class(cls)
