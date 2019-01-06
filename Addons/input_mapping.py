# Input Mapping system.
# Created by: Guilherme Teres Nunes
# Visit: youtube.com/UnidayStudio

import bpy

class INPUT_MAP_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, translate=False, icon_value=85)

class InputMapItem(bpy.types.PropertyGroup):
    key = bpy.props.StringProperty(name="Key",default="")
    value = bpy.props.FloatProperty(name="Value", default=0.0)
    ktype = bpy.props.EnumProperty(items=[
    ('Keyboard','Keyboard','Keyboard input'),
    ('Mouse','Mouse', 'Mouse input'),
    ('Joystick','Joystick','Joystick input')],
    name = "Input Type")
             
class InputMap(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Input",default="New Input Map")
    keys = bpy.props.CollectionProperty(type=InputMapItem)

bge_events = ['ACCENTGRAVEKEY', 'AKEY', 'BACKSLASHKEY', 'BACKSPACEKEY', 'BKEY', 'CAPSLOCKKEY', 'CKEY', 'COMMAKEY', 'DELKEY', 'DKEY', 'DOWNARROWKEY', 'EIGHTKEY', 'EKEY', 'ENDKEY', 'ENTERKEY', 'EQUALKEY', 'ESCKEY', 'F10KEY', 'F11KEY', 'F12KEY', 'F13KEY', 'F14KEY', 'F15KEY', 'F16KEY', 'F17KEY', 'F18KEY', 'F19KEY', 'F1KEY', 'F2KEY', 'F3KEY', 'F4KEY', 'F5KEY', 'F6KEY', 'F7KEY','F8KEY', 'F9KEY', 'FIVEKEY', 'FKEY', 'FOURKEY', 'GKEY', 'HKEY', 'HOMEKEY', 'IKEY', 'INSERTKEY', 'JKEY', 'KKEY', 'LEFTALTKEY', 'LEFTARROWKEY', 'LEFTBRACKETKEY','LEFTCTRLKEY', 'LEFTMOUSE', 'LEFTSHIFTKEY', 'LINEFEEDKEY', 'LKEY', 'MIDDLEMOUSE', 'MINUSKEY', 'MKEY', 'MOUSEX', 'MOUSEY', 'NINEKEY', 'NKEY', 'OKEY', 'ONEKEY', 'OSKEY', 'PAD0', 'PAD1', 'PAD2', 'PAD3', 'PAD4', 'PAD5', 'PAD6', 'PAD7', 'PAD8','PAD9', 'PADASTERKEY', 'PADENTER', 'PADMINUS', 'PADPERIOD', 'PADPLUSKEY', 'PADSLASHKEY', 'PAGEDOWNKEY', 'PAGEUPKEY', 'PAUSEKEY', 'PERIODKEY', 'PKEY', 'QKEY', 'QUOTEKEY', 'RETKEY', 'RIGHTALTKEY', 'RIGHTARROWKEY', 'RIGHTBRACKETKEY', 'RIGHTCTRLKEY', 'RIGHTMOUSE', 'RIGHTSHIFTKEY', 'RKEY', 'SEMICOLONKEY', 'SEVENKEY', 'SIXKEY', 'SKEY', 'SLASHKEY', 'SPACEKEY', 'TABKEY', 'THREEKEY', 'TKEY', 'TWOKEY', 'UKEY', 'UPARROWKEY', 'VKEY', 'WHEELDOWNMOUSE', 'WHEELUPMOUSE', 'WKEY', 'XKEY', 'YKEY', 'ZEROKEY', 'ZKEY']

inputClassTemplate = """
# Input Mapping system.
# Created by: Guilherme Teres Nunes
# Visit: youtube.com/UnidayStudio
import bge

class __InputController():
    def __init__(self, inpList):
        self.inputList = inpList
    
    def __checkInputs(self):
        val = [False, 0.0, False]
        for input in self.inputList:
            origin = None
            if input[0] == "Keyboard":
                origin = bge.logic.keyboard.inputs
            elif input[0] == "Mouse":
                origin = bge.logic.mouse.inputs
            else:
                origin = bge.logic.joysticks[0].inputs
            
            out = origin[ getattr(bge.events, input[1]) ]
            
            if out.active:
                val[1] = input[2]
            if out.activated:
                val[0] = True
            elif out.released:
                val[2] = True
        return val
    
    def value(self):
        return self.__checkInputs()[1]
    
    def getValue(self):
        return self.value()
    
    def pressed(self):
        return self.__checkInputs()[0]
    
    def released(self):
        return self.__checkInputs()[2]
            
            
"""

class InputMapGenerate(bpy.types.Operator):
    bl_idname = "input_map.generate"
    bl_label = "Generate the script"

    def execute(self, context):
        src = inputClassTemplate
        ##
        def convertText(txt):
            return txt.replace(" ", "")
        
        scene = context.scene
        for maps in scene.input_maps:
            mapName = convertText(maps.name)
            inputList = []
            for input in maps.keys:
                keyValue = convertText(input.key).upper()
                
                if keyValue in bge_events:
                    inputList.append([input.ktype, keyValue, input.value])
                    
                elif keyValue + "KEY" in bge_events:
                    inputList.append([input.ktype, keyValue + "KEY", input.value])
                    
                else:
                    print("Error: ", input.key," is not a bge.event!")
            
            src += mapName + " = __InputController(" + str(inputList) + ")\n\n"
        ##
        
        if "InputMapping.py" in bpy.data.texts:
            bpy.data.texts['InputMapping.py'].clear()
            self.report({'INFO'}, "Script Updated!")
        else:
            bpy.data.texts.new("InputMapping.py")
            self.report({'INFO'}, "Script Generated!")
            
        bpy.data.texts['InputMapping.py'].write(src)
        
        return {'FINISHED'}
    
class InputMapAddOperator(bpy.types.Operator):
    bl_idname = "input_map.add"
    bl_label = "Add an item to Input Map"

    def execute(self, context):
        context.scene.input_maps.add()
        context.scene.active_input_map=len(context.scene.input_maps)-1
        return {'FINISHED'}

class InputMapAddKeyOperator(bpy.types.Operator):
    bl_idname = "input_map.addkey"
    bl_label = "Add a key to an Input Map"

    def execute(self, context):        
        a = context.scene.input_maps[context.scene.active_input_map].keys.add()
        return {'FINISHED'}

class InputMapDelKeyOperator(bpy.types.Operator):
    bl_idname = "input_map.delkey"
    bl_label = "Delete a key from an Input Map"
    
    index = bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.input_maps[context.scene.active_input_map].keys.remove(self.index)
        return {'FINISHED'}
    
class InputMapDelOperator(bpy.types.Operator):
    bl_idname = "input_map.del"
    bl_label = "Delete an Input Map item"

    def execute(self, context):        
        context.scene.input_maps.remove(context.scene.active_input_map)
        if( context.scene.active_input_map > 0):
            context.scene.active_input_map-=1
        return {'FINISHED'}

class InputMapPanel(bpy.types.Panel):
    bl_label = "Input Mapping"
    bl_idname = "SCENE_PT_input_mapping"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout 
        scene = context.scene
        row = layout.row()

        col = row.column()
        row.column().template_list("INPUT_MAP_UI", "input_list", scene, "input_maps", scene, "active_input_map") 
        col = row.column()
        col.operator("input_map.add",text="",icon='ZOOMIN')
        col.operator("input_map.del",text="",icon='ZOOMOUT')
                
        if(len(scene.input_maps)>0):
            layout.prop(scene.input_maps[scene.active_input_map], "name",text="Name")
            row = layout.row(True)
            row.operator("input_map.addkey",text="Add Key",icon='ZOOMIN')
            for id,key in enumerate(scene.input_maps[scene.active_input_map].keys):
                box = layout.box().row()
                box.prop(key, "ktype", text="")
                box.prop(key, "key", text="Key")
                box.prop(key, "value", text="")
                box.operator("input_map.delkey",text="",icon='X').index = id
            layout.label(text="Generate or Update the Game Engine Script:")
            layout.operator("input_map.generate",text="Generate Script",icon='FILE_TICK')
        else:
            layout.label(text="There are no inputs!")

bl_info = {
    "name": "UPBGE Input Mapping",
    "description": "Create Input Maps for the UPBGE.",
    "author": "Guilherme Teres Nunes (Uniday Studio)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Scene > Input Mapping",
    "category": "Game Engine"
}

def register():
    bpy.utils.register_class(InputMapGenerate)
    bpy.utils.register_class(InputMapDelKeyOperator)
    bpy.utils.register_class(InputMapAddKeyOperator)
    bpy.utils.register_class(InputMapAddOperator)
    bpy.utils.register_class(InputMapDelOperator)        
    bpy.utils.register_class(InputMapPanel)
    bpy.utils.register_class(INPUT_MAP_UI)
    bpy.utils.register_class(InputMapItem)
    bpy.utils.register_class(InputMap)
    bpy.types.Scene.input_maps = bpy.props.CollectionProperty(type=InputMap)
    bpy.types.Scene.active_input_map = bpy.props.IntProperty(name="Active Input Map", default=0)
    
def unregister():
    bpy.utils.unregister_class(InputMapGenerate)
    bpy.utils.unregister_class(InputMapDelKeyOperator)
    bpy.utils.unregister_class(InputMapAddKeyOperator)
    bpy.utils.unregister_class(InputMapAddOperator)
    bpy.utils.unregister_class(InputMapDelOperator)        
    bpy.utils.unregister_class(InputMapPanel)
    bpy.utils.unregister_class(INPUT_MAP_UI)
    bpy.utils.unregister_class(InputMapItem)
    bpy.utils.unregister_class(InputMap)
    del bpy.types.Scene.input_maps
    del bpy.types.Scene.active_input_map
    