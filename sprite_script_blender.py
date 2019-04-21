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
#scene_key = bpy.data.scenes.keys()[0]

filename_template = "/render-scene-{a}-camera-{b}-frame-{c}"
#Frame length is the number of frames from zero to render
#Frame step is the number of frames to skip in Blender per frame on sheet
frame_lengths = cfg['frame_lengths']
frame_steps = cfg['frame_steps']
if frame_steps == None or frame_lengths == None:
    print("Please specify frame_steps and/or frame_lengths in config.yml to proceed.")

sheet_name = cfg['sheet_name']
if sheet_name == None:
    sheet_name = 'sheet'

if os.path.isfile("{directory}/{filename}.png".format(directory=render_path, filename=sheet_name)):
    os.remove("{directory}/{filename}.png".format(directory=render_path, filename=sheet_name))

images = []
camera_counts = [] #initialize to zero, will count while rendering
frame_counts = []
scene_count = 0 #initialize to zero, will count while rendering

def create_sheet():
    cell_width = 0
    cell_height = 0
    x_offset = 0
    y_offset = 0

    if 'cell_width' in cfg.keys() and cfg['cell_width'] and 'cell_height' in cfg.keys() and cfg['cell_height']:
        cell_width = cfg['cell_width']
        cell_height = cfg['cell_height']
    else:
        first_image_filename = render_path + (filename_template.format(a=0, b=0, c=0)) + '.png'
        image = Image.open(first_image_filename)

        if cell_width == 0:
            cell_width = image.size[0]
        if cell_height == 0:
            cell_height = image.size[1]

    max_end_frame_count = 0
    max_camera_count = 0
    for i in range(0, scene_count):
        end_frame_count = int(frame_lengths[i] / frame_steps[i])
        if end_frame_count > max_end_frame_count:
            max_end_frame_count = end_frame_count
        if camera_counts[i] > max_camera_count:
            max_camera_count = camera_counts[i]

    sheet_width = int(max_end_frame_count * float(cell_width))
    sheet_height = int(cell_height * max_camera_count * scene_count)
    sheet = Image.new('RGBA', (sheet_width, sheet_height))

    for k in range(0, scene_count):
        end_frame_count = int(frame_lengths[k] / frame_steps[k])
        for j in range(0, camera_counts[k]):
            for i in range(0, frame_counts[k][j]):
                filename = render_path + (filename_template.format(a=k, b=j, c=i)) + '.png'
                raw_image = Image.open(filename)
                sheet.paste(raw_image, (i*cell_width, (j*cell_height + k*cell_height*max_camera_count)))

    sheet.save("{directory}/{filename}.png".format(directory=render_path, filename=sheet_name), 'PNG')

for scene_key in bpy.data.scenes.keys():
    end_frame_count = int(float(frame_lengths[scene_count]) / float(frame_steps[scene_count]))
    bpy.context.screen.scene = bpy.data.scenes[scene_key]
    camera_counts.append(0)
    frame_counts.append([])
    for obj in bpy.data.scenes[scene_key].objects:
        if ( obj.type =='CAMERA'):
            bpy.data.scenes[scene_key].camera = obj
            frame_counts[scene_count].append(0)
            for frame_num in range(0, end_frame_count):
                scene = bpy.context.scene
                scene.frame_set(int(frame_num*frame_steps[scene_count]))
                bpy.data.scenes[scene_key].render.image_settings.file_format = 'PNG'
                image_file_path = render_path + (filename_template.format(a = scene_count, b = camera_counts[scene_count], c = frame_counts[scene_count][camera_counts[scene_count]]))
                bpy.data.scenes[scene_key].render.filepath = image_file_path

                bpy.ops.render.render( animation=False, write_still=True )
                frame_counts[scene_count][camera_counts[scene_count]] += 1
            camera_counts[scene_count] += 1
    scene_count += 1


create_sheet()

for k in range(0, scene_count):
    for j in range(0, camera_counts[k]):
        for i in range(0, frame_counts[k][j]):
            raw_image_filename = render_path + (filename_template.format(a=k, b=j, c=i)) + '.png'
            os.remove(raw_image_filename)
