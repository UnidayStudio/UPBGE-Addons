import bge
from collections import OrderedDict


class Platform(bge.types.KX_PythonComponent):
    """When you you a character physics and attempt to make a moving
    platform, you'll immediatelly see that the character will not move
    with the platform object. So simply add this component to every
    platform in your game and it's enough to make it work."""
    
    args = OrderedDict([
        ("Apply Rotation", True)
    ])

    def start(self, args):
        self.applyRot = args["Apply Rotation"]
        
        self._lastPos = self.object.worldPosition.copy()
        self._lastRot = self.object.worldOrientation.to_quaternion()
        
        self.object["platformTag"] = True
        self.object.collisionCallbacks.append(self.onCollision)
        
    def isOnTop(self, object) -> bool:
        origin = object.worldPosition.copy()
        target = origin.copy()
        target.z -= 100
        
        hit,_,_ = object.rayCast(target, origin, 0.0, "platformTag", 1,1,0)
        return hit == self.object
            
    def onCollision(self, object):
        c = bge.constraints.getCharacter(object)
        if not c:
            # This is only necessary for the character physics
            return
        
        if not self.isOnTop(object):
            return
        
        pos = self.object.worldPosition.copy()
        rot = self.object.worldOrientation.to_quaternion()
                
        diff = self._lastRot.inverted() * rot
        
        object.worldPosition += (pos - self._lastPos) * 0.5
        vec1 = object.worldPosition - self.object.worldPosition
        vec2 = diff * vec1
        object.worldPosition += (vec2 - vec1) * 0.5
        
        if self.applyRot:
            objRot1 = object.worldOrientation.to_quaternion()
            objRot2 = objRot1 * diff
            objRot = objRot1.slerp(objRot2, 0.5)
            object.worldOrientation = objRot.to_matrix()
    
    def update(self):
        self._lastPos = self.object.worldPosition.copy()
        self._lastRot = self.object.worldOrientation.to_quaternion()
