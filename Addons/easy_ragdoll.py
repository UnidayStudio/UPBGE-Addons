import bpy
import bmesh
from mathutils import Matrix, Vector

import math

RAGDOLL_SCRIPT = """# Created by Uniday Studio
import bge
from collections import OrderedDict

from mathutils import Vector, Matrix

LINEAR_VELOCITY_GAIN = 40


class RagdollTimer():
    #Medidor de tempo!
    def __init__(self, initialTime=0):
        self._timer = 0
        self.reset()

        self._timer -= initialTime

    def reset(self):
        self._timer = bge.logic.getRealTime()

    def getElapsedTime(self):
        return bge.logic.getRealTime() - self._timer

    def get(self):
        return bge.logic.getRealTime() - self._timer

class Ragdoll(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Active", True),
        ("Time", 0.5),
        ("Lerp Root Transform", 0.5),
    ])
    
    active = False

    def start(self, args):
        self.active = args["Active"]
        self.time  = args["Time"]
        
        self.__rootLerp = args["Lerp Root Transform"]
        
        self.__timer = RagdollTimer(self.time)
        self.__status = self.active
        self.__statusTap = 0
        
        # Force initial behavior
        for obj in self.object.constraints:
            obj.enforce = float(self.active)
                        
        self.__startList = []        
        # Storing the initial transforms of the ragdoll objects
        tmpTransform = self.object.worldTransform.inverted()
        for obj in self.object.constraints:
            out = [None, None]
            if obj.target:
                target = obj.target.parent
                transf = tmpTransform * target.worldTransform
                out = [target, transf]
            self.__startList.append(out)
            
        self.__boneObjects = {}
        for (obj, _) in self.__startList:
            if obj:
                self.__boneObjects[obj.name] = obj
            
        # The root (parent) object
        self.__root = self.object
        while self.__root.parent:
            self.__root = self.__root.parent
            
        rCenter = self.getRagdollCenterTransform()
        self.__rootOffset = rCenter.inverted() * self.__root.worldTransform
        
    def _getObjectName(self, bone):
        return "RagdollPart-" + self.object.name + "-" + bone.name + "-Dynamic"
    
    def getRagdollCenterTransform(self):
        transforms = [obj.worldTransform for (obj, _) in self.__startList if obj]
        
        count = 1       
        out = Matrix.Identity(4)
        for t in transforms:
            factor = 1.0 / count
            out = out.lerp(t, factor)
            count += 1
        return out
    
    def getRagdollCenterPosition(self):
        pos = Vector([0,0,0])
        count = 0
        
        for (obj, _) in self.__startList:
            if obj:
                pos += obj.worldPosition
                count +=1
        
        if count > 0:
            pos /= count
            return pos
        return self.__root.worldPosition
    
    def resetRootTransform(self): 
        # Reset to the ragdoll center
        center = self.getRagdollCenterPosition()
        center += self.__rootOffset * Vector([0,0,0])
        
        cBoxMinZ = abs(self.__root.cullingBox.min.z * self.__root.worldScale.z)
        target = center - Vector([0,0,cBoxMinZ])
        
        self.__root.worldPosition = center
        
        hit, pos, _ = self.__root.rayCast(target, center, 0.0, "", 1, 1, 0, mask=1)
        if hit:
            self.__root.worldPosition.z = pos.z + cBoxMinZ
    
    def resetRagdollTransform(self):
        transform = self.object.worldTransform        
        for channel in self.object.channels:
            bone = channel.bone
            objName = self._getObjectName(bone)
            
            if objName in self.__boneObjects:
                obj = self.__boneObjects[objName]
                pivot = obj.children[0]
                
                pivotSpace = pivot.worldTransform.inverted() * obj.worldTransform
                
                obj.worldTransform = transform * (channel.pose_matrix * pivotSpace)
                
                obj.linearVelocity = [0,0,0]
                obj.angularVelocity = [0,0,0]
                            
    def applyLinearVelocity(self):
        character = bge.constraints.getCharacter(self.__root)
        
        if character:
            dir = character.walkDirection
            
            for (obj, _) in self.__startList:
                if obj:
                    obj.setLinearVelocity(dir * LINEAR_VELOCITY_GAIN)
                  
    def run(self):
        if self.__status != self.active:
            self.__status = self.active
            self.__timer.reset()
            
            if self.active:
                self.__root.suspendPhysics()
                self.__statusTap = 0
                self.resetRagdollTransform()
                
                self.resetRootTransform()
                    
                self.applyLinearVelocity()
                for (obj,_) in self.__startList:
                    obj.restorePhysics()
            else:
                self.__root.restorePhysics()
                for (obj,_) in self.__startList:
                    obj.suspendPhysics()
            
        t = self.__timer.get() / self.time
        if t <= 1.5:
            if not self.active: t = 1.0 - t
            t = min(1.0, max(0.0, t))
            
            for obj in self.object.constraints:
                obj.enforce = t
                
        if self.active:
            self.__statusTap += 1
            if self.__statusTap > 2:
                self.object.update()
            
            self.resetRootTransform()
        else:
            if t > 1.0:
                self.resetRagdollTransform()
    
    def update(self):
        self.run()

"""


class RagdollSpawner:
    def __init__(self, object):
        self.object = object
        self.transform = self.object.matrix_world
        
        # Change this
        self.thickness = 0.4
        self.rotationLimit = 45
        self.minBoneLength = 2
        self.selfCollision = True
        self.cullPhysics = 0.0
        
        self.bpyCube = bpy.data.meshes.new("RagdollCube-" + self.object.name)
        
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(self.bpyCube)
        bm.free()
        
        self.__addedObjects = []
        
    def __addBoneStuff(self, bone, parentObj):
        boneName = "RagdollPart-" + self.object.name + "-" + bone.name
        
        length = bone.length
        head = bone.head_local
        tailDir = (bone.tail_local - bone.head_local).normalized()
        scene = bpy.context.scene
        
        rot = bone.matrix_local.to_euler()
        pos = head + (tailDir * (length / 2))
        
        # Adding the Cube:
        bpy.ops.mesh.primitive_cube_add(location=pos)
        obj = bpy.context.selected_objects[0]
        obj.name = boneName + "-Dynamic"
        obj.scale = Vector([self.thickness, length / 2, self.thickness])
        obj.scale.x *= self.object.scale.x
        obj.scale.y *= self.object.scale.y
        obj.scale.z *= self.object.scale.z
        obj.rotation_euler = rot
        
        obj.select = True
        bpy.context.scene.objects.active = obj
        bpy.ops.object.transform_apply(scale=True)
                
        # Physics
        obj.game.physics_type = "RIGID_BODY"
        obj.game.use_collision_bounds = True
        obj.game.collision_group[1] = True
        obj.game.collision_group[0] = False
        obj.game.collision_mask[1] = self.selfCollision
        obj.hide_render = True
        
        if self.cullPhysics > 0.0:
            obj.game.activity_culling.use_physics = True
            obj.game.activity_culling.physics_radius = self.cullPhysics
        
        if parentObj:
            rb = obj.constraints.new("RIGID_BODY_JOINT")
            rb.target = parentObj
            rb.pivot_type = "CONE_TWIST"
            rb.show_pivot = True
            rb.pivot_y = -(length / 2) * self.object.scale.y
            
            rb.use_linked_collision = not self.selfCollision
            
            rbRot = math.radians(self.rotationLimit)
            rb.use_angular_limit_x = True
            rb.limit_angle_max_x = rbRot
            rb.use_angular_limit_y = True
            rb.limit_angle_max_y = rbRot
            rb.use_angular_limit_z = True
            rb.limit_angle_max_z = rbRot
                
        # Adding the Empty:
        bpy.ops.object.add()
        empty = bpy.context.selected_objects[0]
        empty.name = boneName + "-Empty"
        empty.parent = obj
        empty.scale = self.object.scale
        empty.location = Vector([0, (-length / 2) * self.object.scale.y, 0])
        
        # Adding the armature constraint
        poseBone = self.object.pose.bones.get(bone.name)
        c = poseBone.constraints.get("Copy Transforms")
        if c == None:
            poseBone.constraints.new("COPY_TRANSFORMS")
            c = poseBone.constraints["Copy Transforms"]
        c.target = empty
                
        obj.matrix_world = self.object.matrix_world * obj.matrix_world
        obj.scale = [1,1,1]
        
        self.__addedObjects += [obj, empty]
        
        return obj
        
    def addBone(self, bone, parentObj=None):
        obj = parentObj
        if bone.length > self.minBoneLength:
            obj = self.__addBoneStuff(bone, parentObj)
        
        for child in bone.children:
            self.addBone(child, obj)

    def run(self):
        for bone in self.object.data.bones:
            if bone.parent == None:
                self.addBone(bone)
        
        for obj in self.__addedObjects:
            obj.select = True       
                     

class RagdollSpawnerOperator(bpy.types.Operator):
    bl_idname = "ragdoll.spawn"
    bl_label = "Spawns the Ragdoll for the Selected Armature."
    
    def execute(self, context):
        obj = context.object
        
        if obj.type != "ARMATURE":
            self.report("ERROR", "The selected object MUST be an armature to add the Ragdoll.")
            return {"FINISHED"}        
        
        # Adding the component
        if not "Ragdoll.py" in bpy.data.texts:
            bpy.data.texts.new("Ragdoll.py")
            bpy.data.texts["Ragdoll.py"].write(RAGDOLL_SCRIPT)
            
        if not obj.game.components.get("Ragdoll"):
            bpy.ops.logic.python_component_register(component_name="Ragdoll.Ragdoll")
        
        # Spawning the Ragdoll
        spawner = RagdollSpawner(obj)        
        scene = context.scene
        spawner.thickness =     scene.ragdoll_thickness
        spawner.rotationLimit = scene.ragdoll_rot_limit
        spawner.minBoneLength = scene.ragdoll_min_b_len
        spawner.selfCollision = scene.ragdoll_self_collision
        spawner.cullPhysics     = scene.ragdoll_cull_physics
        spawner.run()        
        
        return {"FINISHED"}
    

class RagdollPanel(bpy.types.Panel):
    bl_label = "Ragdoll Panel"
    bl_idname = "SCENE_ragdoll_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
 
    def draw(self, context):
        layout = self.layout 
        scene = context.scene
        obj = context.object
        
        if obj == None:
            return
        
        box = layout.box()
        row = box.row()
        
        showConfigs = True
        
        if obj.type != "ARMATURE":
            showConfigs = False
            row.label("Only Armatures can have a Ragdoll.")
        
        if showConfigs:
            row.prop(scene, "ragdoll_show_config", text="", icon=["TRIA_RIGHT","TRIA_DOWN"][scene.ragdoll_show_config], emboss=False)
            row.label("Creator Tool")
        
        if scene.ragdoll_show_config and showConfigs:
            row = box.row()
            col = row.column()
                        
            #col.separator()
            
            col.prop(scene, "ragdoll_thickness", text="Thickness")
            col.prop(scene, "ragdoll_rot_limit", text="Rotation Limit")
            col.prop(scene, "ragdoll_min_b_len", text="Min. Bone Length")
            col.prop(scene, "ragdoll_self_collision", text="Self Collision")
            
            col.separator()
            
            col.prop(scene, "ragdoll_cull_physics", text="Culling Radius")
            
            col.separator()
            
            col.operator("ragdoll.spawn", text="Generate Ragdoll", icon="OUTLINER_DATA_ARMATURE")
            
            row = layout.row()
            if obj.game.components.get("Ragdoll"):
                row.label("Note: This Armature already seem to have a Ragdoll.", icon="ERROR")


bl_info = {
    "name": "Easy Ragdoll",
    "description": "Easy Ragdoll creation tool from an Armature and usage in game using a Python Component.",
    "author": "Guilherme Teres Nunes (Uniday Studio)",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Physics > Ragdoll Panel (with an Armature selected)",
    "category": "Game Engine"
}    

def register():
    bpy.types.Scene.ragdoll_show_config = bpy.props.BoolProperty(name="Show Ragdoll Config", default=True)
    bpy.types.Scene.ragdoll_thickness = bpy.props.FloatProperty(name="Ragdoll Thickness", default=0.4)
    bpy.types.Scene.ragdoll_rot_limit = bpy.props.FloatProperty(name="Ragdoll Rotation Limit", default=15)
    bpy.types.Scene.ragdoll_min_b_len = bpy.props.FloatProperty(name="Ragdoll Min Bone Length", default=0.1)
    bpy.types.Scene.ragdoll_cull_physics = bpy.props.FloatProperty(name="Cull Physics", default=0.0)
    bpy.types.Scene.ragdoll_self_collision = bpy.props.BoolProperty(name="Self Collision", default=True)

    bpy.utils.register_class(RagdollSpawnerOperator)
    bpy.utils.register_class(RagdollPanel)


def unregister():
    bpy.utils.unregister_class(RagdollSpawnerOperator)
    bpy.utils.unregister_class(RagdollPanel)
    
    del bpy.types.Scene.ragdoll_show_config
    del bpy.types.Scene.ragdoll_thickness
    del bpy.types.Scene.ragdoll_rot_limit
    del bpy.types.Scene.ragdoll_min_b_len
    del bpy.types.Scene.ragdoll_cull_physics
    del bpy.types.Scene.ragdoll_self_collision