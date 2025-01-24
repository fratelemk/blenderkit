# Run with: blender -b --python create_demo_scene.py

import os
import bpy  # type: ignore
from math import radians
from collections import namedtuple


ENGINE = "BLENDER_EEVEE_NEXT"

START_FRAME = 1
END_FRAME = 200

Light = namedtuple("Light", "name, location, rotation")

lights = [
    Light("Rim Light", (-4, 2, 2), (-90, 0, 45)),
    Light("Key Light", (0, 0, 5), (0, 0, 0)),
    Light("Fill Light", (4, -5, 2), (90, 0, 45)),
]

# Remove all objects in the scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Add Suzanne
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 2))
monkey = bpy.context.object

# Create three-point lighting setup
for light in lights:
    bpy.ops.object.light_add(type="AREA", location=light.location)
    _ = bpy.context.object
    _.data.energy = 100
    _.data.size = 5
    _.rotation_euler = tuple(radians(angle) for angle in light.rotation)
    _.name = light.name

# Animate Suzanne by rotating it along the Z-axis for 200 frames
monkey.rotation_euler = (0, 0, 0)
monkey.keyframe_insert(data_path="rotation_euler", frame=START_FRAME)

# Set rotation at end_frame
monkey.rotation_euler = (0, 0, radians(360))
monkey.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)

# Set background to black and the monkey material to white
bpy.context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (
    0,
    0,
    0,
    1,
)

# Set the render engine
bpy.context.scene.render.engine = ENGINE

# Set camera view and render settings
bpy.ops.object.camera_add(location=(3, -6, 4))
camera = bpy.context.object
camera.rotation_euler = (radians(72), 0, radians(30))
bpy.context.scene.camera = camera

# Set output settings
bpy.context.scene.frame_start, bpy.context.scene.frame_end = START_FRAME, END_FRAME
bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = (
    1920,
    1080,
)

bpy.ops.wm.save_as_mainfile(
    filepath=os.path.join(os.path.expanduser("~"), "demo.blend")
)
