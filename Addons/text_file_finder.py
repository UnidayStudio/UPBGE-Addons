import bpy

def updateTextSlot(self, context):
    active = bpy.data.texts[context.scene.active_text]
    
    for area in bpy.context.screen.areas:
            if area.type == "TEXT_EDITOR":
                area.spaces[0].text = active
                
                
class TextSlot(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Text", default="Text")
    
                
class TEXT_SLOTS_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        outIcon = "TEXT"
        
        txt = bpy.data.texts[item.name].as_string()
        firstLine = txt.split("\n")[0]
        
        if firstLine[:6] == "#icon=":
            outIcon = firstLine[6:]
        elif firstLine[:7] == "//icon=":
            outIcon = firstLine[7:]
            
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()
        
        if not outIcon in icons:
            outIcon = "TEXT"
        
        layout.prop(item, "name", text="", icon=outIcon, emboss=False)
                
class FileFinder(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "File Finder"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        col = row.column()
        
        col.template_list("TEXT_SLOTS_UI", "text_slots_list", bpy.data, "texts", scene, "active_text")
        
        
classes = (
    TextSlot,
    TEXT_SLOTS_UI,
    FileFinder,
)

bl_info = {
    "name": "Text File Finder",
    "description": "Find your text (and script) files easier with this addon. There is no need to keep scrolling over the default blender pop up menu for it anymore.",
    "author": "Guilherme Teres Nunes (Uniday Studio)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Text Editor > Properties tab > File Finder",
    "category": "Game Engine"
}

def register():
    bpy.types.Scene.active_text = bpy.props.IntProperty(name="Sequence", default=0, update=updateTextSlot)
    
    for c in classes:
        bpy.utils.register_class(c)
        
def unregister():
    for obj in classes:
        bpy.utils.unregister_class(obj)
        
    del bpy.types.Scene.active_text
    