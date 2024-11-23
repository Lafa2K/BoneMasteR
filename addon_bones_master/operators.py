import bpy

# Função para adicionar bones nas edges
def AddBonesToEdges(self, context):
    selected_objects = bpy.context.selected_objects

    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

    # Acessando o bone_size diretamente da cena
    bone_size = context.scene.bone_master_size

    for obj in selected_objects:
        if obj.type == 'MESH':
            amt = bpy.data.armatures.new(f"{obj.name}_armature")  # Nome da armadura será o nome do objeto
            rig = bpy.data.objects.new(f"{obj.name}_armature_Object", amt)
            bpy.context.collection.objects.link(rig)

            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')

            parent_bone = amt.edit_bones.new("ROOT")
            parent_bone.head = (0, 0, 0)
            parent_bone.tail = (0, 0, bone_size)

            # Filtra as edges selecionadas no objeto
            selected_edges = [e for e in obj.data.edges if e.select]

            if not selected_edges:
                self.report({'WARNING'}, f"No edges selected for {obj.name}")
                continue

            # Cria um bone para cada edge selecionada
            for idx, edge in enumerate(selected_edges):
                v1 = obj.data.vertices[edge.vertices[0]].co
                v2 = obj.data.vertices[edge.vertices[1]].co

                v1_world = obj.matrix_world @ v1
                v2_world = obj.matrix_world @ v2

                bone_name = f"Bone_{obj.name}_Edge_{idx+1}"
                bone = amt.edit_bones.new(bone_name)
                bone.head = v1_world
                bone.tail = v2_world

                # Define o "parent" para o bone da edge
                bone.parent = parent_bone
                bone.use_connect = False  # Não conecta diretamente ao parent, para ser offset

                # O tamanho do "bone" será ajustado com base na distância entre os vértices da edge
                edge_length = (v2_world - v1_world).length
                bone.tail = bone.head + (v2_world - v1_world).normalized() * edge_length

            self.report({'INFO'}, f"Created bones for edges in {obj.name}")

    return {'FINISHED'}


# Operador para adicionar bones nas edges
class OBJECT_OT_AddBonesToEdges(bpy.types.Operator):
    bl_idname = "object.add_bones_to_edges"
    bl_label = "Add Bone to Edge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return AddBonesToEdges(self, context)


# Função para adicionar bones no pivô com vertex groups
def AddBonesAtPivotsWithRootAndVertexGroups(self, context):
    selected_objects = bpy.context.selected_objects
    
    if not selected_objects:
        self.report({'WARNING'}, "No objects selected!")
        return {'CANCELLED'}

    # Acessando o bone_size diretamente da cena
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


# Operador para adicionar bones no pivô
class OBJECT_OT_AddBonesAtPivots(bpy.types.Operator):
    bl_idname = "object.add_bones_at_pivots"
    bl_label = "Add bones to object Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Acessa a propriedade bone_size diretamente da cena
        bone_size = context.scene.bone_master_size
        return AddBonesAtPivotsWithRootAndVertexGroups(self, context)


# Função para adicionar bones nos vértices selecionados
class OBJECT_OT_AddBonesToVertices(bpy.types.Operator):
    bl_idname = "object.add_bones_to_vertices"
    bl_label = "Add Bone to Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects

        if not selected_objects:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        # Acessando o bone_size diretamente da cena
        bone_size = context.scene.bone_master_size

        for obj in selected_objects:
            if obj.type == 'MESH':
                amt = bpy.data.armatures.new(f"{obj.name}_armature")  # Nome da armadura será o nome do objeto
                rig = bpy.data.objects.new(f"{obj.name}_armature_Object", amt)
                bpy.context.collection.objects.link(rig)

                bpy.ops.object.mode_set(mode='OBJECT')

                bpy.context.view_layer.objects.active = rig
                bpy.ops.object.mode_set(mode='EDIT')

                parent_bone = amt.edit_bones.new("ROOT")
                parent_bone.head = (0, 0, 0)
                parent_bone.tail = (0, 0, bone_size)

                # Filtra os vértices selecionados no objeto
                selected_vertices = [v for v in obj.data.vertices if v.select]

                if not selected_vertices:
                    self.report({'WARNING'}, f"No vertices selected for {obj.name}")
                    continue

                # Cria um bone para cada vértice selecionado
                for idx, vertex in enumerate(selected_vertices):
                    vertex_position = obj.matrix_world @ vertex.co

                    bone_name = f"Bone_{obj.name}_Vertex_{idx+1}"
                    bone = amt.edit_bones.new(bone_name)

                    # O head do osso é a posição do vértice
                    bone.head = vertex_position

                    # O tail será a posição do vértice + bone_size ao longo do eixo Z
                    bone.tail = (vertex_position[0], vertex_position[1], vertex_position[2] + bone_size)

                    # Define o "parent" para o bone da root
                    bone.parent = parent_bone
                    bone.use_connect = False  # Não conecta diretamente ao parent, para ser offset

                self.report({'INFO'}, f"Created bones for selected vertices in {obj.name}")

        return {'FINISHED'}


# Função de registro
def register():
    # Verifique se a classe já foi registrada antes de registrar novamente
    if not hasattr(bpy.types, "OBJECT_OT_AddBonesAtPivots"):
        bpy.utils.register_class(OBJECT_OT_AddBonesAtPivots)

    if not hasattr(bpy.types, "OBJECT_OT_AddBonesToEdges"):
        bpy.utils.register_class(OBJECT_OT_AddBonesToEdges)

    # Novo operador
    if not hasattr(bpy.types, "OBJECT_OT_AddBonesToVertices"):
        bpy.utils.register_class(OBJECT_OT_AddBonesToVertices)

    # Definindo a propriedade bone_master_size na cena global
    bpy.types.Scene.bone_master_size = bpy.props.FloatProperty(
        name="Bone Size",
        description="Bone Size",
        default=0.05,
        min=0.01,
        max=1.0
    )


def unregister():
    # Remover classes ao desregistrar
    if hasattr(bpy.types, "OBJECT_OT_AddBonesAtPivots"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesAtPivots)

    if hasattr(bpy.types, "OBJECT_OT_AddBonesToEdges"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesToEdges)

    # Novo operador
    if hasattr(bpy.types, "OBJECT_OT_AddBonesToVertices"):
        bpy.utils.unregister_class(OBJECT_OT_AddBonesToVertices)

    # Remover a propriedade bone_master_size da cena
    del bpy.types.Scene.bone_master_size
