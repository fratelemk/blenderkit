import bpy
import numpy as np


SOURCE_OBJECT   = "Rectangle"

FALLBACK_RADIUS = 1.0    # used when SOURCE_OBJECT is empty / not found
FALLBACK_POINTS = 300    # points on the fallback circle

# Sphere-collision repulsion
# Increase REPULSION_RADIUS to get larger / fewer lobes.
# Decrease it for more, tighter folds.
REPULSION_RADIUS   = 1.2
REPULSION_STRENGTH = 0.5

# Edge spring — keeps perimeter length constant (the key constraint)
# Higher = more rigid curve, less stretching between layers
SPRING_STRENGTH = 4

# Alignment — mild smoothing to prevent numerical kinks
ALIGNMENT_STRENGTH = 0.10

# Timestep — keep small; large values cause instability
DT = 0.1

# Inner-radius floor — no point comes closer than this to the centroid.
# Prevents folds from pinching all the way to the centre.
# Set relative to INITIAL_RADIUS (e.g. 0.4 = 40 % of starting radius).
MIN_INNER_RADIUS = 0.75

# Vase dimensions
NUM_LAYERS   = 60   # one layer = one simulation step
LAYER_HEIGHT = 0.06  # vertical gap between tube centres

# Memory — chunked repulsion to cap peak RAM
CHUNK_SIZE = 64      # peak RAM per step ≈ CHUNK_SIZE × INITIAL_POINTS × 16 B

# Tube (bevel) geometry
TUBE_RADIUS     = 0.034  # cross-section radius  (set ≈ LAYER_HEIGHT × 0.55)
TUBE_RESOLUTION = 12     # segments around the circle cross-section


def _seed_points() -> np.ndarray:
    """Return (N, 2) seed points from SOURCE_OBJECT, or a fallback circle."""
    obj = bpy.data.objects.get(SOURCE_OBJECT) if SOURCE_OBJECT else None

    if obj is None:
        if SOURCE_OBJECT:
            print(f"  Warning: object '{SOURCE_OBJECT}' not found — using fallback circle.")
        angles = np.linspace(0, 2 * np.pi, FALLBACK_POINTS, endpoint=False)
        return np.column_stack([FALLBACK_RADIUS * np.cos(angles),
                                FALLBACK_RADIUS * np.sin(angles)])

    if obj.type == 'CURVE':
        pts = []
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for bp in spline.bezier_points:
                    co = obj.matrix_world @ bp.co
                    pts.append((co.x, co.y))
            else:  # POLY or NURBS
                for bp in spline.points:
                    co = obj.matrix_world @ bp.co.xyz
                    pts.append((co.x, co.y))

    elif obj.type == 'MESH':
        pts = []
        for v in obj.data.vertices:
            co = obj.matrix_world @ v.co
            pts.append((co.x, co.y))

    else:
        print(f"  Warning: '{SOURCE_OBJECT}' is type '{obj.type}', not CURVE or MESH — using fallback circle.")
        angles = np.linspace(0, 2 * np.pi, FALLBACK_POINTS, endpoint=False)
        return np.column_stack([FALLBACK_RADIUS * np.cos(angles),
                                FALLBACK_RADIUS * np.sin(angles)])

    pts = np.array(pts, dtype=float)
    print(f"  Seed: '{obj.name}' ({obj.type})  →  {len(pts)} points")
    return pts


def simulate() -> list:
    pts = _seed_points()

    # Rest length = mean edge length of the seed (conserved throughout).
    # Using the mean handles seeds with uneven vertex spacing.
    edges       = np.linalg.norm(np.diff(np.vstack([pts, pts[0]]), axis=0), axis=1)
    rest_length = float(edges.mean())
    print(f"  Rest length: {rest_length:.4f}  ({len(pts)} points)")

    layers = [pts.copy()]

    for i in range(NUM_LAYERS - 1):
        pts = _step(pts, rest_length)
        layers.append(pts.copy())
        print(f"  Layer {i + 2:3d}/{NUM_LAYERS}")

    return layers


def _step(pts: np.ndarray, rest_length: float) -> np.ndarray:
    n      = len(pts)
    forces = np.zeros_like(pts)

    # 1. Sphere-collision repulsion (chunked to cap peak memory)
    for start in range(0, n, CHUNK_SIZE):
        end   = min(start + CHUNK_SIZE, n)
        chunk = pts[start:end]
        diff  = chunk[:, np.newaxis, :] - pts[np.newaxis, :, :]   # (C, N, 2)
        dist  = np.linalg.norm(diff, axis=2)                      # (C, N)
        local = np.arange(end - start)
        dist[local, local + start] = np.inf                        # ignore self
        in_range  = dist < REPULSION_RADIUS
        safe_dist = np.where(in_range, dist, 1.0)
        strength  = np.where(in_range,
                             (REPULSION_RADIUS - dist) / REPULSION_RADIUS, 0.0)
        forces[start:end] += (
            diff / safe_dist[:, :, np.newaxis] * strength[:, :, np.newaxis]
        ).sum(axis=1) * REPULSION_STRENGTH

    # 2. Rigid edge spring — resist any deviation from rest_length
    prev_idx = (np.arange(n) - 1) % n
    next_idx = (np.arange(n) + 1) % n
    to_prev  = pts[prev_idx] - pts
    to_next  = pts[next_idx] - pts
    d_prev   = np.linalg.norm(to_prev, axis=1, keepdims=True)
    d_next   = np.linalg.norm(to_next, axis=1, keepdims=True)
    forces  += SPRING_STRENGTH * (to_prev / (d_prev + 1e-5)) * (d_prev - rest_length)
    forces  += SPRING_STRENGTH * (to_next / (d_next + 1e-5)) * (d_next - rest_length)

    # 3. Alignment — smooth out numerical kinks
    forces += ((pts[prev_idx] + pts[next_idx]) * 0.5 - pts) * ALIGNMENT_STRENGTH

    new_pts = pts + forces * DT

    # 4. Inner-radius floor — push any point that crossed inward back out
    centroid  = new_pts.mean(axis=0)
    to_center = new_pts - centroid
    radii     = np.linalg.norm(to_center, axis=1, keepdims=True)
    too_close = (radii < MIN_INNER_RADIUS) & (radii > 1e-5)
    new_pts   = np.where(too_close,
                         centroid + to_center / radii * MIN_INNER_RADIUS,
                         new_pts)

    return new_pts


def build_curves(layers: list):
    for name in ("DiffGrowthVase",):
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["DiffGrowthVase"], do_unlink=True)
        if name in bpy.data.curves:
            bpy.data.curves.remove(bpy.data.curves["DiffGrowthVase"])

    curve_data              = bpy.data.curves.new("DiffGrowthVase", type='CURVE')
    curve_data.dimensions   = '3D'
    curve_data.bevel_depth  = TUBE_RADIUS
    curve_data.bevel_resolution = TUBE_RESOLUTION
    curve_data.use_fill_caps    = False

    for i, pts in enumerate(layers):
        z      = i * LAYER_HEIGHT
        spline = curve_data.splines.new('POLY')
        spline.use_cyclic_u = True
        spline.points.add(len(pts) - 1)
        for j, p in enumerate(pts):
            spline.points[j].co = (p[0], p[1], z, 1.0)

    obj = bpy.data.objects.new("DiffGrowthVase", curve_data)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mat  = bpy.data.materials.get("VaseMat") or bpy.data.materials.new("VaseMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.85, 0.80, 0.72, 1.0)
        bsdf.inputs["Roughness"].default_value  = 0.35
    if not obj.data.materials:
        obj.data.materials.append(mat)

    return obj


layers = simulate()
obj = build_curves(layers)
