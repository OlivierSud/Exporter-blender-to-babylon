bl_info = {
    'name': 'babylon.js',
    'author': 'Olivier Sudermann',
    'version': (5, 0, 0),
    'blender': (4, 0, 0),
    'location': 'File > Export > babylon.js (.json)',
    'description': 'Export babylon.js scenes (.json)',
    'wiki_url': 'https://github.com/OlivierSud/Exporter-blender-to-babylon',
    'tracker_url': 'https://oliviersudermann.wixsite.com/olivier-sudermann',
    'category': 'babylon.JS'}

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper

# allow module to be changed during a session (dev purposes)
if "bpy" in locals():
    print('Reloading .json exporter')
    import imp
    if 'materials' in locals():
        imp.reload(materials)  # directory
    if 'animation' in locals():
        imp.reload(animation)
    if 'armature' in locals():
        imp.reload(armature)
    if 'camera' in locals():
        imp.reload(camera)
    if 'f_curve_animatable' in locals():
        imp.reload(f_curve_animatable)
    if 'js_exporter' in locals():
        imp.reload(js_exporter)
    if 'light_shadow' in locals():
        imp.reload(light_shadow)
    if 'logging' in locals():
        imp.reload(logging)
    if 'mesh' in locals():
        imp.reload(mesh)
    if 'package_level' in locals():
        imp.reload(package_level)
    if 'shape_key_group' in locals():
        imp.reload(shape_key_group)
    if 'sound' in locals():
        imp.reload(sound)
    if 'world' in locals():
        imp.reload(world)

#===============================================================================
class JsonMain(bpy.types.Operator, ExportHelper):
    bl_idname = 'export.json'
    bl_label = 'Export babylon.js scene' # used on the label of the actual 'save' button
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = '.json'            # used as the extension on file selector

    filepath: bpy.props.StringProperty(subtype = 'FILE_PATH') # assigned once the file selector returns
    filter_glob: bpy.props.StringProperty(name='.json',default='*.json;*.babylon.js', options={'HIDDEN'})
    export_selected: bpy.props.BoolProperty(
        name='Export only selected objects',
        description='Export only the currently selected objects',
        default=False
    )
    
    file_extension_type: bpy.props.EnumProperty(
        name='File Extension',
        description='Choose the file extension for the exported file',
        items=[
            ('JSON', '.json', 'Export as .json file'),
            ('BABYLON', '.babylon.js', 'Export as .babylon.js file'),
            ('CUSTOM', 'Custom', 'Use a custom file extension')
        ],
        default='JSON'
    )
    
    custom_extension: bpy.props.StringProperty(
        name='Custom Extension',
        description='Custom file extension (without the dot)',
        default='json'
    )

    def execute(self, context):
        from .json_exporter import JsonExporter
        from .package_level import get_title, verify_min_blender_version
        from .shader_disconnect import disconnect_all_shaders, reconnect_all_shaders
        import os

        if not verify_min_blender_version():
            self.report({'ERROR'}, 'version of Blender too old.')
            return {'FINISHED'}

        # Determine the file extension based on user selection
        if self.file_extension_type == 'JSON':
            extension = '.json'
        elif self.file_extension_type == 'BABYLON':
            extension = '.babylon.js'
        else:  # CUSTOM
            extension = self.custom_extension
            if not extension.startswith('.'):
                extension = '.' + extension
        
        # Update the filepath with the selected extension
        filepath_base = os.path.splitext(self.filepath)[0]
        self.filepath = filepath_base + extension

        # Disconnect all shaders BEFORE any export processing
        disconnect_count = disconnect_all_shaders()
        print(f'Disconnected {disconnect_count} shader(s) from Material Output')

        try:
            exporter = JsonExporter()
            objects = bpy.context.selected_objects if self.export_selected else bpy.context.scene.objects
            exporter.execute(context, self.filepath, objects)

            if (exporter.fatalError):
                self.report({'ERROR'}, exporter.fatalError)

            elif (exporter.nErrors > 0):
                self.report({'ERROR'}, 'Output cancelled due to data error, See log file.')

            elif (exporter.nWarnings > 0):
                self.report({'WARNING'}, 'Processing completed, but ' + str(exporter.nWarnings) + ' WARNINGS were raised,  see log file.')

        finally:
            # Reconnect all shaders AFTER export is complete
            reconnect_count = reconnect_all_shaders()
            print(f'Reconnected {reconnect_count} shader(s) to Material Output')

        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(
            text='Other export settings in properties panels'
        )
        self.layout.prop(self, 'export_selected')
        
        # File extension selection
        self.layout.separator()
        self.layout.label(text='File Extension:')
        self.layout.prop(self, 'file_extension_type', expand=True)
        
        # Show custom extension field only when Custom is selected
        if self.file_extension_type == 'CUSTOM':
            self.layout.prop(self, 'custom_extension')
#===============================================================================
# The list of classes which sub-class a Blender class, which needs to be registered
from . import camera
from . import light_shadow
from . import materials # directory
from . import world # must be defined before mesh
from . import mesh
classes = (
    # Operator sub-classes
    JsonMain,

    # Panel sub-classes
    camera.BJS_PT_CameraPanel,
    light_shadow.BJS_PT_LightPanel,
    materials.material.BJS_PT_MaterialsPanel,
    mesh.BJS_PT_MeshPanel,
    world.BJS_PT_WorldPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

# Registration the calling of the INFO_MT_file_export file selector
def menu_func(self, context):
    from .package_level import get_title
    # the info for get_title is in this file, but getting it the same way as others
    self.layout.operator(JsonMain.bl_idname, text=get_title())

if __name__ == '__main__':
    unregister()
    register()
