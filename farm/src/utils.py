import bpy  # type: ignore
import json
import sys
import subprocess
from collections import deque


def render(blend_file, scene):
    args = ["blender", "-b", blend_file, "-a", "-S", scene]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    content = deque()
    while True:
        line = process.stdout.readline().decode()
        content.append(line)
        if line == "" and process.poll() is not None:
            break

    process.wait()
    print(content)


def split_frames(start, end, n_hosts):
    total_frames = end - start + 1
    chunk_size = total_frames // n_hosts
    remainder = total_frames % n_hosts

    frame_chunks = []
    current_start = start

    for _ in range(n_hosts):
        current_end = current_start + chunk_size - 1

        if remainder > 0:
            current_end += 1
            remainder -= 1

        frame_chunks.append((current_start, current_end))
        current_start = current_end + 1

    return frame_chunks


def get_scene_metadata():
    filepath = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.open_mainfile(filepath=filepath)

    metadata = []
    for scene in bpy.data.scenes:
        metadata.append(
            {
                scene.name: {
                    "frame_start": scene.frame_start,
                    "frame_end": scene.frame_end,
                    "resolution_x": scene.render.resolution_x,
                    "resolution_y": scene.render.resolution_y,
                    "resolution_percentage": scene.render.resolution_percentage,
                }
            }
        )

    return json.dumps(metadata)
