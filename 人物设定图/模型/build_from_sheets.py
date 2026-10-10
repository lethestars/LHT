"""Loft a body from the T-pose sheets and the side view, then preview it.

Front and back images share the same framing. Side depth comes from 侧面.jpg,
aligned by height. The preview paints the front sheet onto the mesh so we can
check that the model is the same character before rigging.
"""

import json
import os

import numpy as np
from PIL import Image

ROOT = "/workspace/人物设定图"
OUT = os.path.join(ROOT, "模型")
HEIGHT = 1.90
N_RING = 28


def load_mask(path, thresh=28):
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image)
    bg = arr[0, 0].astype(np.int16)
    mask = np.abs(arr.astype(np.int16) - bg).sum(2) > thresh
    return mask, arr


def segments(row):
    xs = np.where(row)[0]
    if len(xs) == 0:
        return []
    segs = []
    start = prev = int(xs[0])
    for x in xs[1:]:
        x = int(x)
        if x > prev + 2:
            segs.append((start, prev))
            start = x
        prev = x
    segs.append((start, prev))
    return segs


def ring(cx, cy, rx, ry, z, n=N_RING):
    """Horizontal cross-section, lofted along Z."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack(
        [cx + rx * np.cos(t), cy + ry * np.sin(t), np.full(n, z)],
        axis=1,
    )


def arm_ring(x, cy, cz, ry, rz, n=N_RING):
    """Vertical cross-section, lofted along X."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.stack(
        [np.full(n, x), cy + ry * np.cos(t), cz + rz * np.sin(t)],
        axis=1,
    )


def cap(center, normal_sign, radii_ring):
    """Triangle fan. radii_ring is (n, 3)."""
    n = len(radii_ring)
    c = np.array(center, dtype=np.float64)
    faces = []
    start = None
    return c, [
        (0, i, (i + 1) % n) if normal_sign > 0 else (0, (i + 1) % n, i)
        for i in range(n)
    ]


def connect(index_a, index_b, n, flip=False):
    faces = []
    for i in range(n):
        j = (i + 1) % n
        if not flip:
            faces.append((index_a + i, index_a + j, index_b + j))
            faces.append((index_a + i, index_b + j, index_b + i))
        else:
            faces.append((index_a + i, index_b + j, index_a + j))
            faces.append((index_a + i, index_b + i, index_b + j))
    return faces


def build():
    front_m, front_rgb = load_mask(os.path.join(ROOT, "T字正面.jpg"))
    back_m, back_rgb = load_mask(os.path.join(ROOT, "T字背面.jpg"))
    side_m, side_rgb = load_mask(os.path.join(ROOT, "侧面.jpg"))
    fh, fw = front_m.shape
    ys, xs = np.where(front_m)
    top = int(ys.min())
    # The sheet has a caption under the feet. Cut at the empty gap above it.
    bot = int(ys.max())
    empty = 0
    for y in range(top, fh):
        if front_m[y].sum() < 40:
            empty += 1
            if empty > 8 and y > top + 400:
                bot = y - empty
                break
        else:
            empty = 0
    front_m[bot + 1 :] = False
    span = bot - top
    scale = HEIGHT / span
    cx = 0.5 * (xs.min() + xs.max())

    sys_, sxs = np.where(side_m)
    stop, sbot = int(sys_.min()), int(sys_.max())
    sspan = sbot - stop
    sscale = HEIGHT / sspan

    def side_edges(norm):
        y = int(np.clip(stop + norm * sspan, stop, sbot - 1))
        cols = np.where(side_m[y])[0]
        if len(cols) < 2:
            return None
        return int(cols.min()), int(cols.max())

    # Anchor side X so the waist center sits on y = 0. Larger image X is the front,
    # which is Blender -Y.
    waist = side_edges(0.40)
    anchor = 0.5 * (waist[0] + waist[1])

    def side_y(norm):
        edges = side_edges(norm)
        if edges is None:
            return -0.08, 0.08
        y_front = -(edges[1] - anchor) * sscale
        y_back = -(edges[0] - anchor) * sscale
        return y_front, y_back

    # Arm band: rows much wider than the torso, in the upper body.
    row_w = []
    for y in range(top, bot + 1):
        segs = segments(front_m[y])
        row_w.append(max((b - a) for a, b in segs) if segs else 0)
    row_w = np.array(row_w)
    arm_thresh = 0.62 * row_w.max()
    arm_rows = np.where(row_w > arm_thresh)[0]
    arm_y0 = top + int(arm_rows.min())
    arm_y1 = top + int(arm_rows.max())

    # Torso width taken from the chest just under the arms.
    chest_y = min(bot - 1, arm_y1 + 18)
    chest_segs = segments(front_m[chest_y])
    chest_segs.sort(key=lambda s: s[1] - s[0], reverse=True)
    torso_x0, torso_x1 = chest_segs[0]

    # Leg split. Ignore one-pixel gaps and specks; require a run of rows
    # that really are two legs.
    split_y = None
    run = 0
    for y in range(arm_y1 + 40, bot):
        segs = [s for s in segments(front_m[y]) if s[1] - s[0] > 12]
        if len(segs) >= 2:
            run += 1
            if run >= 6:
                split_y = y - 5
                break
        else:
            run = 0
    if split_y is None:
        raise RuntimeError("leg split not found")

    verts = []
    faces = []

    def add_loft(rings, close_start=False, close_end=False):
        base = len(verts)
        n = N_RING
        for r in rings:
            verts.extend(r.tolist())
        for i in range(len(rings) - 1):
            faces.extend(connect(base + i * n, base + (i + 1) * n, n))
        if close_start:
            c = rings[0].mean(axis=0)
            c[2] = rings[0][0, 2]
            ci = len(verts)
            verts.append(c.tolist())
            for i in range(n):
                faces.append((ci, base + (i + 1) % n, base + i))
        if close_end:
            c = rings[-1].mean(axis=0)
            ci = len(verts)
            verts.append(c.tolist())
            b = base + (len(rings) - 1) * n
            for i in range(n):
                faces.append((ci, b + i, b + (i + 1) % n))

    # Torso and head, one ring every 2 pixels. Through the arm band, keep only
    # the torso width so the arms can be lofts of their own.
    rings = []
    y = top
    while y <= split_y + 8:
        norm = (y - top) / span
        z = (bot - y) * scale
        segs = segments(front_m[y])
        if not segs:
            y += 2
            continue
        if arm_y0 <= y <= arm_y1:
            x0 = max(torso_x0 - 6, 0)
            x1 = min(torso_x1 + 6, fw - 1)
            # Delts flare: blend toward the full shoulder width near the arm root.
            width_px = x1 - x0
        else:
            segs.sort(key=lambda s: s[1] - s[0], reverse=True)
            x0, x1 = segs[0]
            width_px = x1 - x0
        y_front, y_back = side_y(norm)
        # Keep a minimum depth so slices never collapse.
        if y_back - y_front < 0.04:
            mid = 0.5 * (y_front + y_back)
            y_front, y_back = mid - 0.02, mid + 0.02
        cx_m = (0.5 * (x0 + x1) - cx) * scale
        rx = max(0.5 * width_px * scale, 0.012)
        ry = 0.5 * (y_back - y_front)
        cy = 0.5 * (y_front + y_back)
        rings.append(ring(cx_m, cy, rx, ry, z))
        y += 2
    add_loft(rings, close_start=True, close_end=False)
    hip_z = (bot - (split_y + 8)) * scale

    # Legs.
    def leg_rings(which):
        rings = []
        y = split_y - 36
        while y <= bot:
            segs = segments(front_m[y])
            if len(segs) < 2:
                y += 2
                continue
            segs.sort(key=lambda s: s[0])
            x0, x1 = segs[0] if which == "right" else segs[-1]
            # Image x grows to the viewer's right, which is the character's left
            # when he faces the camera. Keep that screen axis as mesh +X.
            norm = (y - top) / span
            z = (bot - y) * scale
            y_front, y_back = side_y(norm)
            cx_m = (0.5 * (x0 + x1) - cx) * scale
            rx = max(0.5 * (x1 - x0) * scale, 0.01)
            ry = max(0.5 * (y_back - y_front) * 0.55, rx * 0.85)
            cy = 0.5 * (y_front + y_back)
            rings.append(ring(cx_m, cy, rx, ry, z))
            y += 2
        return rings

    for which in ("right", "left"):
        lr = leg_rings(which)
        if len(lr) > 2:
            add_loft(lr, close_start=False, close_end=True)

    # Arms, lofted along X. Thickness is the vertical run of the mask.
    def arm_rings(sign):
        """sign +1 is image-right / mesh +X."""
        rings = []
        if sign > 0:
            x_start = torso_x1 - 28
            x_end = int(xs.max())
            step = 2
        else:
            x_start = torso_x0 + 28
            x_end = int(xs.min())
            step = -2
        x = x_start
        while (x <= x_end) if step > 0 else (x >= x_end):
            col = front_m[arm_y0 : arm_y1 + 1, np.clip(x, 0, fw - 1)]
            ys_local = np.where(col)[0]
            if len(ys_local) >= 2:
                y0 = arm_y0 + int(ys_local.min())
                y1 = arm_y0 + int(ys_local.max())
                thick = max((y1 - y0) * scale, 0.02)
                z = (bot - 0.5 * (y0 + y1)) * scale
                mx = (x - cx) * scale
                # Arms sit slightly in front of the ribcage.
                rings.append(arm_ring(mx, -0.015, z, thick * 0.48, thick * 0.5))
            x += step
        return rings

    for sign in (1, -1):
        ar = arm_rings(sign)
        if len(ar) > 2:
            add_loft(ar, close_start=False, close_end=True)

    verts = np.array(verts, dtype=np.float64)
    faces = np.array(faces, dtype=np.int32)

    # Landmarks in mesh space for the armature.
    def z_at(norm):
        return (1 - norm) * HEIGHT

    shoulder_z = (bot - 0.5 * (arm_y0 + arm_y1)) * scale
    chest_z = (bot - chest_y) * scale
    landmarks = {
        "height": HEIGHT,
        "shoulder_z": float(shoulder_z),
        "chest_z": float(chest_z),
        "hip_z": float(hip_z),
        "split_z": float((bot - split_y) * scale),
        "scale": float(scale),
        "center_x_px": float(cx),
        "top": int(top),
        "bot": int(bot),
        "fw": int(fw),
        "fh": int(fh),
        "arm_y0": int(arm_y0),
        "arm_y1": int(arm_y1),
        "side_anchor": float(anchor),
        "side_scale": float(sscale),
        "side_top": int(stop),
        "side_span": int(sspan),
        "side_w": int(side_m.shape[1]),
        "side_h": int(side_m.shape[0]),
    }
    os.makedirs(OUT, exist_ok=True)
    np.savez(os.path.join(OUT, "body_mesh.npz"), verts=verts, faces=faces)
    with open(os.path.join(OUT, "landmarks.json"), "w") as f:
        json.dump(landmarks, f, indent=2)
    write_obj(os.path.join(OUT, "body.obj"), verts, faces)
    preview(verts, faces, front_rgb, landmarks)
    print("verts", len(verts), "faces", len(faces))
    print(json.dumps(landmarks, indent=2))
    return verts, faces, landmarks


def write_obj(path, verts, faces):
    with open(path, "w") as f:
        for v in verts:
            f.write(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}\n")
        for tri in faces:
            f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")


def preview(verts, faces, image, landmarks):
    h, w = image.shape[:2]
    scale = landmarks["scale"]
    cx = landmarks["center_x_px"]
    bot = landmarks["bot"]
    buf = np.full((h, w, 3), 90, dtype=np.uint8)
    zbuf = np.full((h, w), -1e9, dtype=np.float32)
    # Paint front-facing triangles (normal Y < 0) with the sheet color.
    for tri in faces:
        p = verts[tri]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        if n[1] >= 0:
            continue
        pix = np.stack(
            [
                p[:, 0] / scale + cx,
                bot - p[:, 2] / scale,
            ],
            axis=1,
        )
        shade(buf, zbuf, pix, p[:, 1], image)
    out = Image.fromarray(buf)
    path = "/opt/cursor/artifacts/mesh-preview-front.png"
    out.save(path)
    print("preview", path)


def shade(buf, zbuf, pix, depth, image):
    h, w = buf.shape[:2]
    # Bounding box raster.
    minx = max(int(np.floor(pix[:, 0].min())), 0)
    maxx = min(int(np.ceil(pix[:, 0].max())), w - 1)
    miny = max(int(np.floor(pix[:, 1].min())), 0)
    maxy = min(int(np.ceil(pix[:, 1].max())), h - 1)
    if minx >= maxx or miny >= maxy:
        return
    v0, v1, v2 = pix
    den = (v1[1] - v2[1]) * (v0[0] - v2[0]) + (v2[0] - v1[0]) * (v0[1] - v2[1])
    if abs(den) < 1e-8:
        return
    ys = np.arange(miny, maxy + 1)
    xs = np.arange(minx, maxx + 1)
    xx, yy = np.meshgrid(xs, ys)
    w0 = ((v1[1] - v2[1]) * (xx - v2[0]) + (v2[0] - v1[0]) * (yy - v2[1])) / den
    w1 = ((v2[1] - v0[1]) * (xx - v2[0]) + (v0[0] - v2[0]) * (yy - v2[1])) / den
    w2 = 1 - w0 - w1
    inside = (w0 >= -0.01) & (w1 >= -0.01) & (w2 >= -0.01)
    if not inside.any():
        return
    z = w0 * depth[0] + w1 * depth[1] + w2 * depth[2]
    region = zbuf[miny : maxy + 1, minx : maxx + 1]
    update = inside & (z > region)
    if not update.any():
        return
    # Sample the sheet at the pixel itself: the mesh is built from this mask,
    # so a matching outline means the character lands on the character.
    region_img = buf[miny : maxy + 1, minx : maxx + 1]
    sample = image[miny : maxy + 1, minx : maxx + 1]
    region_img[update] = sample[update]
    region[update] = z[update]


if __name__ == "__main__":
    build()
