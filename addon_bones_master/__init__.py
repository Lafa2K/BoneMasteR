bl_info = {
    "name": "Bone Master",
    "description": "Add bones to the pivots of selected objects with ROOT and Vertex Groups | Adicionar bones nos pivôs de objetos selecionados com ROOT e Vertex Groups",
    "author": "Lafa2k + ChatGpt",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N Panel > BoneMaster",
    "category": "Object",
    "wiki_url": "github.com/Lafa2K/BoneMasteR",
}


import bpy
from . import operators, panels

# Registrar classes
def register():
    operators.register()
    panels.register()

def unregister():
    operators.unregister()
    panels.unregister()

if __name__ == "__main__":
    register()
