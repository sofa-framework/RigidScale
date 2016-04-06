import os

import Sofa

import Compliant.sml
import SofaPython.sml

from Compliant import Tools
from Compliant.Tools import cat as concat

import RigidScale.sml

__file = __file__.replace('\\', '/') # windows

#=============================================================
# Creation of the articulated body systeme
#=============================================================
def createScene(root):

    # global parameters
    root.createObject('VisualStyle', displayFlags="showVisual showBehavior showWireframe hideCollisionModels" )
    root.dt = 0.01
    root.gravity = [0, 0, 0]

    root.createObject('RequiredPlugin', pluginName='image')
    root.createObject('RequiredPlugin', pluginName='Flexible')
    root.createObject('RequiredPlugin', pluginName='Compliant')
    root.createObject('RequiredPlugin', pluginName='Registration')
    root.createObject('RequiredPlugin', pluginName='RigidScale')

    # Script launch
    root.createObject('PythonScriptController', name='script', filename=__file, classname='MyClass')

# ================================================================= #
# Creation of the scene
# ================================================================= #
class MyClass(Sofa.PythonScriptController):

    def createGraph(self, root):

        # Variable
        self.t = 0
        self.root_node = root

        # scene setting
        self.root_node.gravity = '0 0 0'

        # Background color
        root.createObject('BackgroundSetting', color='1 1 1')

        # Attach setting
        root.createObject('CompliantAttachButtonSetting' )

        # solver
        #root.createObject('CompliantPseudoStaticSolver', iterations="10", threshold="1e-5", velocityFactor="0", printLog=False, stabilization=1, neglecting_compliance_forces_in_geometric_stiffness=False)
        root.createObject('CompliantImplicitSolver', stabilization=1)
        root.createObject('SequentialSolver', iterations=50, precision=1E-15, iterateOnBilaterals=1)
        root.createObject('LDLTResponse', schur=0)

        # sml scene
        self.model = SofaPython.sml.Model(os.path.join(os.path.dirname(__file__), "./data/main.sml"))
        self.scene = RigidScale.sml.SceneArticulatedRigidScale(root, self.model)

        # settings
        self.scene.param.elasticity = 1E5
        self.scene.param.voxelSize = 0.025
        self.scene.param.jointCompliance = 1E-6
        self.scene.param.constraintCompliance = 1E-6

        # visual settings
        self.scene.param.showRigid=True
        self.scene.param.showRigidScale=0.025
        self.scene.param.showOffset=True
        self.scene.param.showOffsetScale=0.020
        self.scene.param.showRigidDOFasSphere=False

        # scene creation
        self.scene.createScene()

        boneToFixed = ['s_humerus']
        # Add of fixed constraint
        for b in boneToFixed:
            if b in self.scene.bones.keys():
                self.scene.bones[b].rigidNode.createObject('FixedConstraint', fixAll=0, indices='1')
                self.scene.bones[b].scaleNode.createObject('FixedConstraint', fixAll=0, indices='1')

    # To remove warning
    def onBeginAnimationStep(self, dt):
        if self.t==0:
            for bone in self.scene.bones.values():
                bone.affineMassNode.active = False
        self.t = self.t+dt

