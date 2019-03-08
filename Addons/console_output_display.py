# Console Output Display Add-on.
# Created by: Guilherme Teres Nunes
# Visit: youtube.com/UnidayStudio

import bpy
import sys
import io

class Thief(io.StringIO):
    def __init__(self, initial):
        super().__init__()
        self.source = initial

def organizeMessage(inp):
    txt = inp.split("\n")
    out = []
    
    tmp = []
    lastI = -999
    for line in txt:
        i = len(out) - 1
        
        flag = False
        while i >= 0 and i > lastI:       
            if out[i] == line:
                tmp.append(line)
                lastI = i
                flag = True
                break
            
            i -= 1
            
        
        if lastI == i and i == len(out)-1:
            div = len(out)-len(tmp) 
            if isinstance(out[div-1], int):
                out[div-1] += 1
            else:
                out.insert(div, 2)
                
            tmp = []
            lastI = -999
        elif not flag:
            tmp.append(line)
            out += tmp
            tmp = []
    return out
    
    
class ClearConsoleOperator(bpy.types.Operator):
    bl_idname = "console_output.clear"
    bl_label = "Clears the Console."
    
    def execute(self, context):
        if isinstance(sys.stdout, Thief):
            sys.stdout = Thief(sys.stdout.source)
        else:
            sys.stdout = Thief(sys.stdout)
                
        if isinstance(sys.stderr, Thief):
            sys.stderr = Thief(sys.stderr.source)
        else:
            sys.stderr = Thief(sys.stderr)
            
        #sys.stdout = Thief()
        #sys.stderr = Thief()
        
        return {"FINISHED"}
        

class Panel(bpy.types.Panel):
    bl_label = "Game Engine: Console Output"
    bl_idname = "SCENE_console_output"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
 
    def draw(self, context):
        layout = self.layout 
        scene = context.scene
        row = layout.row()
        
        col = row.column()
        
        
        col.prop(scene, "console_thief", text="Display Console output")
        
        # 
        if scene.console_thief:
            if not isinstance(sys.stdout, Thief):
                sys.stdout = Thief(sys.stdout)
                
            if not isinstance(sys.stderr, Thief):
                sys.stderr = Thief(sys.stderr)
        else:
            if isinstance(sys.stdout, Thief):
                sys.stdout = sys.stdout.source
                
            if isinstance(sys.stderr, Thief):
                sys.stderr = sys.stderr.source
            return
        
        col.separator()        
        
        col.prop(scene, "show_outputs", text="Show Debug outputs")
        col.prop(scene, "show_errors", text="Show Errors") 
        
        col.operator("console_output.clear", text="Clear Console Outputs", icon="FILE_REFRESH")
        
        col.separator()
        
        
        
        # Prints
        if scene.show_outputs:
            val = organizeMessage( sys.stdout.getvalue() )
                        
            if len(val) > 0:
                if not isinstance(val[0], int):
                    box = col.box()
                    box.label(text="Output:", icon="TEXT")
                for obj in val:
                    if isinstance(obj, int):
                        box = col.box()
                        box.label(text="("+str(obj)+") Outputs:", icon="TEXT")
                    else:
                        box.label(text=obj)
            else:
                col.label(text="No Debug output to show")
        
        if scene.show_errors:
            val = organizeMessage( sys.stderr.getvalue() )
            
            if len(val) > 0:
                if not isinstance(val[0], int):
                    box = col.box()
                    box.label(text="Error:", icon="CANCEL")
                for obj in val:
                    if isinstance(obj, int):
                        box = col.box()
                        box.label(text="("+str(obj)+") Errors:", icon="CANCEL")
                    else:
                        box.label(text=obj)
            else:
                col.label(text="No error to show")
   
bl_info = {
    "name": "Console Output Display",
    "description": "Displays the Game Engine Console outputs in a friendly way inside Blender UI.",
    "author": "Guilherme Teres Nunes (Uniday Studio)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Scene > Game Engine: Console Output",
    "category": "Game Engine"
}         
        
def register():
    bpy.types.Scene.show_outputs = bpy.props.BoolProperty(name="Show outputs", default=True)
    bpy.types.Scene.show_errors = bpy.props.BoolProperty(name="Show errors", default=True)
    bpy.types.Scene.console_thief = bpy.props.BoolProperty(name="Show Console", default=False)

    bpy.utils.register_class(Panel)
    bpy.utils.register_class(ClearConsoleOperator)

def unregister():
    bpy.utils.unregister_class(Panel)
    bpy.utils.unregister_class(ClearConsoleOperator)
    
    del bpy.types.Scene.show_outputs
    del bpy.types.Scene.show_errors
    del bpy.types.Scene.console_thief