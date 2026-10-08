"""High-angle clay: right fist around shaft, left pinch on left nipple."""
from PIL import Image, ImageDraw

src = (
    r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets"
    r"\c__Users_92982_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"-19c355fc_images_image-13b30c19-a84d-4da8-bf9c-f69a6f21090e.png"
)
out_guide = r"C:\Users\92982\Desktop\LHT\openpose\36_highangle_nipple_stroke_guide.png"
out_canny = r"C:\Users\92982\Desktop\LHT\openpose\36_highangle_nipple_stroke_canny.png"
out_paint = r"C:\Users\92982\Desktop\LHT\openpose\36_highangle_PAINT_HERE.png"

im = Image.open(src).convert("RGBA")
w, h = im.size  # 607 x 1024

# --- landmarks (his left = viewer's right) ---
l_nipple = (358, 348)  # his LEFT pec
r_shoulder = (95, 290)
l_shoulder = (500, 305)
groin = (278, 575)
# shaft from above: base at fly, tip toward camera (up the abs)
shaft_base = (278, 605)
shaft_mid = (282, 545)
shaft_tip = (286, 495)
r_fist = (282, 555)

guide = im.copy()
gd = ImageDraw.Draw(guide, "RGBA")
canny = Image.new("RGB", (w, h), (0, 0, 0))
cd = ImageDraw.Draw(canny)


def line(pts, fill, width, canny_w=None):
    gd.line(pts, fill=fill, width=width, joint="curve")
    cd.line(pts, fill=(255, 255, 255), width=canny_w or max(2, width - 1), joint="curve")


def oval(box, outline, width):
    gd.ellipse(box, outline=outline, width=width)
    cd.ellipse(box, outline=(255, 255, 255), width=width)


# ===== RIGHT ARM: shoulder -> down inside -> fist around shaft =====
# upper arm (his right, viewer's left)
line([(98, 300), (85, 390), (110, 460)], (40, 180, 255, 255), 6, 4)
# forearm into groin
line([(110, 460), (170, 520), (230, 545), (260, 555)], (40, 180, 255, 255), 6, 4)
# full-wrap fist: RING around mid shaft (hollow)
oval([r_fist[0] - 42, r_fist[1] - 28, r_fist[0] + 42, r_fist[1] + 34], (40, 180, 255, 255), 4)
# knuckles in FRONT of shaft (row of 4 small rings)
knuckles = [
    (r_fist[0] - 28, r_fist[1] - 6),
    (r_fist[0] - 8, r_fist[1] - 14),
    (r_fist[0] + 12, r_fist[1] - 12),
    (r_fist[0] + 30, r_fist[1] - 2),
]
for kx, ky in knuckles:
    oval([kx - 12, ky - 11, kx + 12, ky + 13], (40, 180, 255, 255), 3)
# thumb wrap from his right (viewer's left)
oval([r_fist[0] - 48, r_fist[1] + 4, r_fist[0] - 10, r_fist[1] + 32], (40, 180, 255, 255), 3)

# ===== SHAFT: hollow vertical, base at crotch, tip toward camera =====
oval([shaft_tip[0] - 22, shaft_tip[1] - 16, shaft_tip[0] + 22, shaft_tip[1] + 20], (255, 80, 40, 255), 3)
line(
    [(shaft_tip[0] - 20, shaft_tip[1] + 8), (shaft_base[0] - 26, shaft_base[1] - 6)],
    (255, 80, 40, 255),
    3,
)
line(
    [(shaft_tip[0] + 20, shaft_tip[1] + 8), (shaft_base[0] + 26, shaft_base[1] - 6)],
    (255, 80, 40, 255),
    3,
)
oval([shaft_base[0] - 28, shaft_base[1] - 14, shaft_base[0] + 28, shaft_base[1] + 18], (255, 80, 40, 255), 3)
# scrotum under base (hollow)
oval([shaft_base[0] - 34, shaft_base[1] + 8, shaft_base[0] + 34, shaft_base[1] + 48], (255, 80, 40, 255), 3)

# ===== LEFT ARM: shoulder -> elbow out -> hand on LEFT pec =====
# upper arm
line([(498, 318), (530, 390), (500, 430)], (80, 220, 80, 255), 6, 4)
# forearm in to left nipple
line([(500, 430), (450, 400), (400, 365), (370, 352)], (80, 220, 80, 255), 6, 4)
# pinch hand: thumb + index on nipple, not a fist
nx, ny = l_nipple
# palm
oval([nx - 8, ny - 6, nx + 36, ny + 28], (80, 220, 80, 255), 3)
# index pinch from above
oval([nx - 16, ny - 18, nx + 8, ny + 6], (80, 220, 80, 255), 3)
# thumb pinch from below
oval([nx - 6, ny + 8, nx + 18, ny + 28], (80, 220, 80, 255), 3)
# other fingers curled
for i, (fx, fy) in enumerate([(nx + 18, ny - 4), (nx + 28, ny + 4), (nx + 32, ny + 14)]):
    oval([fx - 9, fy - 8, fx + 9, fy + 10], (80, 220, 80, 255), 2)
# nipple mark
oval([nx - 7, ny - 7, nx + 7, ny + 7], (255, 220, 40, 255), 2)

# labels
try:
    from PIL import ImageFont

    font = ImageFont.truetype("arial.ttf", 22)
except Exception:
    font = None
gd.text((20, 20), "R hand: FULL FIST stroke", fill=(40, 180, 255, 255), font=font)
gd.text((250, 20), "L hand: PINCH L nipple", fill=(80, 220, 80, 255), font=font)
gd.text((20, 50), "camera: HIGH looking down", fill=(255, 255, 255, 255), font=font)

guide.convert("RGB").save(out_guide)
canny.save(out_canny)

# paint-here: white bg + clay faint + same lines
paint = Image.new("RGB", (w, h), (255, 255, 255))
clay = im.convert("RGB")
# faint body
faint = Image.blend(paint, clay, 0.35)
pd = ImageDraw.Draw(faint)
# copy canny lines in black for painting
bw = canny.convert("L")
for y in range(h):
    row = [bw.getpixel((x, y)) for x in range(w)]
    for x, v in enumerate(row):
        if v > 200:
            faint.putpixel((x, y), (0, 0, 0))
faint.save(out_paint)

print("saved")
print(out_guide)
print(out_canny)
print(out_paint)
print("size", w, h)
