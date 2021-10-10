# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Probe Vizualization",
    "author" : "Kemal BAL",
    "description" : "kemalbal00@gmail.com",
    "blender" : (2, 92, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy, re

class ObjectMoveX(bpy.types.Operator):
    """My Object Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.move_x"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Move X by One"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):        # execute() is called when running the operator.

        # The original script
        scene = context.scene
        for obj in scene.objects:
            obj.location.x += 1.0

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.


class ProbeVizualization(bpy.types.Operator):
        """Probe Vizualization"""     
        bl_idname = "object.probe_vizualization"        
        bl_label = "Probe Vizualization"       
        bl_options = {'REGISTER', 'UNDO'}  

        print('test')
        filepath = bpy.props.StringProperty(subtype="FILE_PATH") 

        def execute(self, context):
            self.master_collection = bpy.context.scene.collection
            self.probe_collection = bpy.data.collections.new('Probe Collection')
            self.master_collection.children.link(self.probe_collection)
            probes = probes_parser(self.filepath, 'flow3d')
            for prob in probes.probes:
                self.addProbe(prob.position[0],prob.position[1],prob.position[2], prob.id)

            return {'FINISHED'}

        def addProbe(self, x, y, z, name = ''):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=.01, enter_editmode=False, location=(float(x), float(y), float(z)))
            self.probe_collection.objects.link(bpy.context.object)
            self.master_collection.objects.unlink(bpy.context.object)
            bpy.context.object.name = 'probe' + str(name)

        def invoke(self, context, event): 
            context.window_manager.fileselect_add(self) 

            return {'RUNNING_MODAL'}  

class saveProbs(bpy.types.Operator):
        """Save Probes"""     
        bl_idname = "object.save_probe"        
        bl_label = "Save Probes"       
        bl_options = {'REGISTER', 'UNDO'}  

        directory = bpy.props.StringProperty(
            name="Outdir Path",
            description="Where I will save probes"
            )
        def execute(self, context):
            file = open(self.directory + 'probes.txt', 'w')
            probe_content = ''

            self.probe_collection = bpy.data.collections['Probe Collection']
            for probe in self.probe_collection.objects:
                probe_content  = probe_content + '(' + str(round(probe.location[0],3)) + ' ' + str(round(probe.location[1],3)) + ' ' + str(round(probe.location[2],3)) + ')\n'

            file.write(probe_content)
            return {'FINISHED'}

        def invoke(self, context, event):
            context.window_manager.fileselect_add(self)

            return {'RUNNING_MODAL'}

def register():
    print('register')
    bpy.utils.register_class(ProbeVizualization)
    bpy.utils.register_class(saveProbs)
    bpy.utils.register_class(ObjectMoveX)

def unregister():
    print('unregister')
    bpy.utils.unregister_class(ProbeVizualization)
    bpy.utils.unregister_class(saveProbs)
    bpy.utils.unregister_class(ObjectMoveX)


class probes_parser:
    def __init__(self, fileName, type = 'openfoam'):
        self.type = type
        self.fileName = fileName
        self.probes = []
        self.openFile()

    def openFile(self):
        with open(self.fileName) as file_in:
            counter = 0
            x = 0
            y = 0
            z = 0

            for line in file_in:
                str = line.strip() 

                if(self.type == 'openfoam'):
                    probe_properties = re.findall(r'\(([-+]?\d*\.?\d+) ([-+]?\d*\.?\d+) ([-+]?\d*\.?\d+)\)', str)
                    if probe_properties:
                        probe_properties = probe_properties[0]
                        counter = counter + 1
                        new_probe = probes(counter, probe_properties)
                        self.probes.append(new_probe)
                if(self.type == 'flow3d'):
                    probe_properties = re.findall(r'(\w)loc\((\d*)\)=([-+]?\d*\.?\d+)', str)
                    if probe_properties:
                        probe_properties = probe_properties[0]
                        if(probe_properties[0] == 'x'):
                            x = probe_properties[2]
                        if(probe_properties[0] == 'y'):
                            y = probe_properties[2]
                        if(probe_properties[0] == 'z'):
                            z = probe_properties[2]
                        if(x != 0 and y != 0 and z != 0):
                            new_probe = probes(probe_properties[1], [x,y,z])
                            self.probes.append(new_probe)
                            x = 0
                            y = 0
                            z = 0
                
                      
class probes:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.values = []

    def add_value(self, value):
        self.values.append(value)

    def average_value(self, index):
        count = len(self.values)
        sum = 0
        for p in self.values:
            sum += float(p["value"][index])
        return sum / count
            
if __name__ == "__main__":
    register()