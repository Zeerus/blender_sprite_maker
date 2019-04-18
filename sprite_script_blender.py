import bpy
import os
from PIL import Image
import yaml

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#Set path to output renders
if 'render_output_dir' in cfg.keys() and cfg['render_output_dir']:
        render_path = cfg['render_output_dir']
else:
    script_directory = os.path.dirname(os.path.realpath(__file__))
    render_path = script_directory + "/render"

#Deselect items in blend file
bpy.ops.object.select_all(action='DESELECT')

#Grab the first scene
scene_key = bpy.data.scenes.keys()[0]

filename_template = "/render-{a}-frame-{b}"
#Frame length is the number of frames from zero to render
#Frame step is the number of frames to skip in Blender per frame on sheet
frame_length = cfg['frame_length']
if frame_length == None:
    frame_length = 1

frame_step = cfg['frame_step']
if frame_step == None:
    frame_step = 1

end_frame_count = int(frame_length / frame_step)

sheet_name = cfg['sheet_name']
if sheet_name == None:
    sheet_name = 'sheet'

images = []
camera_count = 0 #initialize to zero, will count while rendering

def create_sheet():
    cell_width = 0
    cell_height = 0
    x_offset = 0
    y_offset = 0

    if 'cell_width' in cfg.keys() and cfg['cell_width'] and 'cell_height' in cfg.keys() and cfg['cell_height']:
        cell_width = cfg['cell_width']
        cell_height = cfg['cell_height']
    else:
        first_image_filename = render_path + (filename_template.format(a = 0, b = 0)) + '.png'
        image = Image.open(first_image_filename)

        if cell_width == 0:
            cell_width = image.size[0]
        if cell_height == 0:
            cell_height = image.size[1]

    sheet_width = int(end_frame_count * float(cell_width))
    sheet_height = int(cell_height * camera_count)
    sheet = Image.new('RGBA', (sheet_width, sheet_height))

    for i in range(0, end_frame_count):
            for j in range(0, camera_count):
                filename = render_path + (filename_template.format(a = j, b = i)) + '.png'
                raw_image = Image.open(filename)
                sheet.paste(raw_image, (i*cell_width, j*cell_height))

    sheet.save("{directory}/{filename}.png".format(directory=render_path, filename=sheet_name), 'PNG')

for obj in bpy.data.objects:
    if ( obj.type =='CAMERA'):
        bpy.data.scenes[scene_key].camera = obj

        for f in range(0, end_frame_count):
            scene = bpy.context.scene
            scene.frame_set(f*frame_step)
            bpy.data.scenes[scene_key].render.image_settings.file_format = 'PNG'
            image_file_path = render_path + (filename_template.format(a = camera_count, b = f))
            bpy.data.scenes[scene_key].render.filepath = image_file_path

            bpy.ops.render.render( animation=False, write_still=True )
        camera_count += 1


create_sheet()

for i in range(0, end_frame_count):
    for j in range(0, camera_count):
        raw_image_filename = render_path + (filename_template.format(a = j, b = i)) + '.png'
        os.remove(raw_image_filename)
