import bpy

# No painel
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
        layout.separator()

        layout.operator("object.add_bones_at_pivots", text="Add bones to object Origin")
        layout.operator("object.add_bones_to_edges", text="Add Bone to Edge")
        layout.separator()
        layout.prop(scene, "bone_to_vertex_normal", text="Bone to Vertex Normal")
        layout.operator("object.add_bones_to_vertices", text="Add Bone to Vertex")


def register():
    bpy.types.Scene.bone_to_vertex_normal = bpy.props.BoolProperty(
        name="Bone to Vertex Normal",
        description="Adjust bone rotation to vertex normal",
        default=False
    )
    
    bpy.types.Scene.bone_master_size = bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )

    # Registrando as classes
    bpy.utils.register_class(VIEW3D_PT_BonesMasterPanel)

def unregister():
    del bpy.types.Scene.bone_to_vertex_normal
    del bpy.types.Scene.bone_master_size
    
    bpy.utils.unregister_class(VIEW3D_PT_BonesMasterPanel)

if __name__ == "__main__":
    register()
