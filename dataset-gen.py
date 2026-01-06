import bpy
import mathutils
import os
import random
import math
from datetime import datetime
import uuid
import json

# -------------------------------
# SETTINGS
# -------------------------------
# Read from environment variable (no argparse!)
print(f"DEBUG: NUM_SAMPLES environment variable = '{os.getenv('NUM_SAMPLES')}'")
print(f"DEBUG: All environment variables: {list(os.environ.keys())}")

NUM_SAMPLES = int(os.getenv("NUM_SAMPLES", "23000"))
print(f"Rendering {NUM_SAMPLES} views headlessly...")

# Object to rotate
OBJ_NAME = "Sketchfab_model"
obj = bpy.data.objects.get(OBJ_NAME)
if obj is None:
    raise ValueError(f"Object '{OBJ_NAME}' not found in scene.")
obj.rotation_mode = 'QUATERNION'

# Container object for lights reference
container = bpy.data.objects.get("isotope_container")

# Lights to randomize
light_names = ["Point.001", "Point.002", "Point.003"]

# -------------------------------
# CREATE UNIQUE DATASET FOLDER
# -------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, "output")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_id = str(uuid.uuid4())[:8]
dataset_name = f"rotated_sketchfab_{timestamp}_{unique_id}"
dataset_dir = os.path.join(BASE_DIR, dataset_name)
images_dir = os.path.join(dataset_dir, "images")
os.makedirs(images_dir, exist_ok=True)

# -------------------------------
# QUATERNION GENERATOR (Marsaglia)
# -------------------------------
def marsaglia_quaternion():
    while True:
        u1, u2 = random.uniform(-1,1), random.uniform(-1,1)
        if u1**2 + u2**2 < 1: break
    while True:
        u3, u4 = random.uniform(-1,1), random.uniform(-1,1)
        if u3**2 + u4**2 < 1: break
    q = mathutils.Quaternion((u1, u2, u3, u4))
    q.normalize()
    return q

quat_generator = (marsaglia_quaternion() for _ in range(NUM_SAMPLES))

# -------------------------------
# LIGHT RANDOMIZATION
# -------------------------------
def random_light_position(radius_min=3, radius_max=3.5, phi_min=1.5, phi_max=1.6):
    theta = random.uniform(0, 2*math.pi)
    phi = random.uniform(phi_min, phi_max)
    r = random.uniform(radius_min, radius_max)
    x = r*math.sin(phi)*math.cos(theta)
    y = r*math.sin(phi)*math.sin(theta)
    z = r*math.cos(phi)
    return container.location + mathutils.Vector((x, y, z)) if container else mathutils.Vector((x, y, z))

def randomize_lights():
    for name in light_names:
        light = bpy.data.objects.get(name)
        if light:
            light.location = random_light_position()

# -------------------------------
# RENDER LOOP
# -------------------------------
for render_index in range(NUM_SAMPLES):
    quat = next(quat_generator)
    obj.rotation_quaternion = quat
    randomize_lights()
    bpy.context.view_layer.update()
    w, x, y, z = quat.w, quat.x, quat.y, quat.z
    filename = f"model_w{w:.3f}_x{x:.3f}_y{y:.3f}_z{z:.3f}_{datetime.now().strftime('%H%M%S%f')}.png"
    filepath = os.path.join(images_dir, filename)
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    if (render_index + 1) % 100 == 0:
        print(f"Rendered {render_index+1}/{NUM_SAMPLES}")

print(f"All renders complete! Images saved to {images_dir}")

# -------------------------------
# METADATA
# -------------------------------
metadata = {
    "artifact_type": "dataset",
    "dataset_name": dataset_name,
    "dataset_version": "v1.0",
    "generated_at": datetime.utcnow().isoformat(),
    "num_samples": NUM_SAMPLES,
    "generator": {
        "blender_version": bpy.app.version_string,
        "script_name": os.path.basename(__file__),
        "object_name": obj.name,
        "lights": light_names
    }
}
metadata_path = os.path.join(images_dir, "metadata.json")
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata saved to {metadata_path}")