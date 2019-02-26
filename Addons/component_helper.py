# Component Helper Addon.
# Created by: Guilherme Teres Nunes
# Visit: youtube.com/UnidayStudio

import bpy

src_comments = """import bge
from collections import OrderedDict

class %s(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        # Put your initialization code here, args stores the values from the UI.
        # self.object is the owner object of this component.
        pass

    def update(self):
        # Put your code executed every logic step here.
        # self.object is the owner object of this component.
        pass
    """

src_no_comments = """import bge
from collections import OrderedDict

class %s(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        pass

    def update(self):
        pass
"""

############################################################################################

class ComponentList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Component",default="")

class ComponentListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        script = item.name.split(".")[0]+".py"
        classNm = item.name.split(".")[1]
        
        #layout.label(text=item.name, translate=False, icon="GAME")
        layout.label(text=classNm, translate=False, icon="GAME")
        layout.label(text=script, translate=False, icon="TEXT")
        
        
        
############################################################################################

class ReloadAllOperator(bpy.types.Operator):
    bl_idname = "component_helper.reload"
    bl_label = "Reloads the components of all the objects in the Scene."
    
    def execute(self, context):
        updated = 0
        act = bpy.context.scene.objects.active

        for obj in bpy.context.scene.objects:
            flag = obj.select
            
            obj.select = True
            bpy.context.scene.objects.active = obj
            
            for i, comp in enumerate(obj.game.components):
                bpy.ops.logic.python_component_reload(index = i)
                updated += 1
                
            obj.select = flag
            
        bpy.context.scene.objects.active = act
        
        print(updated," Components updated!")
        return {"FINISHED"}
    
class AddComponentOperator(bpy.types.Operator):
    bl_idname = "component_helper.add"
    bl_label = "Add or create a new Component."
    
    def execute(self, context):
        nm = context.scene.component_list[context.scene.component_list_active].name
        
        bpy.ops.logic.python_component_register(component_name=nm)
        
        return {"FINISHED"}
    
class CreateComponentOperator(bpy.types.Operator):
    bl_idname = "component_helper.create"
    bl_label = "Add or create a new Component."
    
    def execute(self, context):        
        script = context.scene.comp_new_script.replace(" ","").replace(".py","")+".py"
        classNm = context.scene.comp_new_class.replace(" ","")
        
        if script in bpy.data.texts:
            self.report({"ERROR"}, "Script '"+script+"' already exists.")
            return {"FINISHED"}
        else:
            bpy.data.texts.new(script)
            self.report({"INFO"}, "Script '"+script+"' generated!")
            
        if context.scene.comp_new_comments:
            bpy.data.texts[script].write(src_comments % classNm)
        else:
            bpy.data.texts[script].write(src_no_comments % classNm)
            
        if context.scene.comp_new_assign:
            nm = script[:-3]+"."+classNm
            
            bpy.ops.logic.python_component_register(component_name=nm)
        #bpy.ops.logic.python_component_create(component_name=nm)
        
        return {"FINISHED"}
    
    
class RefreshComponentOperator(bpy.types.Operator):
    bl_idname = "component_helper.refresh"
    bl_label = "Refresh the Component List"
    
    def execute(self, context):
        scene = context.scene
        
        scene.component_list.clear()
        
        for obj in bpy.data.texts:
            if obj.name[-3:] == ".py":
                strTxt = obj.as_string()
                if "bge.types.KX_PythonComponent" in strTxt:
                    for line in strTxt.split("\n"):
                        if "bge.types.KX_PythonComponent" in line:
                            nm = line.replace("class", "").replace(" ","").split("(")[0]
                            
                            item = scene.component_list.add()
                            item.name = obj.name[:-3]+"."+nm
                
        return {"FINISHED"}


class UtilComponentsPanel(bpy.types.Panel):
    bl_label = "Component Helper"
    bl_idname = "LOGIC_EDITOR_Util_Components"
    bl_space_type = 'LOGIC_EDITOR'
    bl_region_type = 'UI'
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout 
        scene = context.scene
        row = layout.row()

        col = row.column()
        
        pie = col.column(True)
        
        col2 = pie.box().column()
        
        row = col2.row()
        row.prop(scene, "component_list_show", text="", icon=["TRIA_RIGHT","TRIA_DOWN"][scene.component_list_show], emboss=False)
        row.label(text="Existing components")
        
        if scene.component_list_show:
            row.operator("component_helper.refresh", text="", icon="FILE_REFRESH")
            
            col2.template_list("ComponentListUI", "component_list_ui", scene,"component_list", scene, "component_list_active")
            
            #pie  /  col2
            pie.operator("component_helper.add", text="Add Selected Component", icon="ZOOMIN")
                    
        col.separator()  
        
        pie = col.column(True)
        col3 = pie.box().column()
        row = col3.row()
        
        row.prop(scene, "component_creator_show", text="", icon=["TRIA_RIGHT","TRIA_DOWN"][scene.component_creator_show], emboss=False)
        row.label(text="Create component")
        
        if scene.component_creator_show:
            #cl = row.column()
            pie2 = col3.box().column()
            
            pie2.prop(scene, "comp_new_script", text="Script name", icon="TEXT")
            pie2.prop(scene, "comp_new_class", text="Class name", icon="GAME")
            
            pie2.separator()
            
            pie2.prop(scene, "comp_new_comments", text="Include comments")
            pie2.prop(scene, "comp_new_assign", text="Assign to active object")
            
            #col3.separator()
            
            #pie  /  col3
            pie.operator("component_helper.create", text="Create a new Component", icon="NEW")
        
        col.separator()    
        
        col.operator("component_helper.reload", text="Reload All Scene Components", icon="RECOVER_LAST")
        
        
       
classes = (
    UtilComponentsPanel,
    ReloadAllOperator,
    AddComponentOperator,
    ComponentListUI,
    ComponentList,
    RefreshComponentOperator,
    CreateComponentOperator
)


bl_info = {
    "name": "UPBGE Component Helper",
    "description": "With addon will help you to handle the UPBGE Python Components (for game logic).",
    "author": "Guilherme Teres Nunes (Uniday Studio)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Logic Editor > Properties tab > Component Helper",
    "category": "Game Engine"
}
        
def register():
    for obj in classes:
        bpy.utils.register_class(obj)
        
    bpy.types.Scene.component_list_show = bpy.props.BoolProperty(name="Show Available Components", default=True)
    bpy.types.Scene.component_creator_show = bpy.props.BoolProperty(name="Show Component Creator", default=False)
    
    bpy.types.Scene.comp_new_script = bpy.props.StringProperty(name="New Script Name", default="module")
    bpy.types.Scene.comp_new_class = bpy.props.StringProperty(name="New Class Name", default="Component")
    
    bpy.types.Scene.comp_new_comments = bpy.props.BoolProperty(name="Include Comments", default=False)
    bpy.types.Scene.comp_new_assign = bpy.props.BoolProperty(name="Auto assign to object", default=True)
    
    bpy.types.Scene.component_list = bpy.props.CollectionProperty(type=ComponentList)
    bpy.types.Scene.component_list_active = bpy.props.IntProperty(name="Active Component Selection", default=0)
    
    
    
def unregister():
    for obj in classes:
        bpy.utils.unregister_class(obj)
        
    del bpy.types.Scene.component_list_show
    del bpy.types.Scene.component_creator_show
    
    del bpy.types.Scene.comp_new_script
    del bpy.types.Scene.comp_new_class
    
    del bpy.types.Scene.comp_new_comments
    del bpy.types.Scene.comp_new_assign
    
    del bpy.types.Scene.component_list
    del bpy.types.Scene. component_list_active
    