from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

src = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\vr_room_pole_crotch.jpg"
out_color = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\vr_room_fullgrip_guide.jpg"
out_canny = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\vr_room_fullgrip_canny.png"

im = Image.open(src).convert("RGBA")
w, h = im.size

# approximate cylinder axis from zipper toward camera (center)
cx, y_base, y_tip = 430, 880, 560
r = 48  # cylinder radius at mid

# cover the old pinching hand with a local smear of nearby abdomen/shorts
cover = Image.new("RGBA", im.size, (0, 0, 0, 0))
cd = ImageDraw.Draw(cover)
# sample a skin-ish fill
cd.ellipse([cx - 160, 620, cx + 90, 900], fill=(196, 130, 95, 230))
cover = cover.filter(ImageFilter.GaussianBlur(12))
base = Image.alpha_composite(im, cover)

ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)

# vertical cylinder (empty-looking with rim)
for i, yy in enumerate(range(y_tip, y_base, 3)):
    t = (yy - y_tip) / (y_base - y_tip)
    rr = int(r * (0.85 + 0.2 * t))
    shade = int(150 + 30 * t)
    d.ellipse([cx - rr, yy - 10, cx + rr, yy + 18], fill=(shade, shade + 4, shade + 8, 255))
# tip cap
d.ellipse([cx - int(r * 0.85), y_tip - 18, cx + int(r * 0.85), y_tip + 22], fill=(190, 194, 198, 255))

# FULL WRAP FIST around mid shaft
fy = 710
# palm / near knuckles in front (lower-left of cylinder from viewer)
# back of hand
d.ellipse([cx - 95, fy - 55, cx + 70, fy + 85], fill=(210, 155, 120, 255))
# four knuckles as a row in FRONT of the tube, hiding far side
knuckles = [
    (cx - 55, fy - 10),
    (cx - 18, fy - 22),
    (cx + 18, fy - 18),
    (cx + 50, fy - 4),
]
for i, (kx, ky) in enumerate(knuckles):
    d.ellipse([kx - 28, ky - 26, kx + 28, ky + 32], fill=(205, 148, 112, 255))
    d.ellipse([kx - 14, ky - 18, kx + 16, ky + 8], fill=(185, 125, 95, 255))
# thumb wrapping from the right, overlapping
d.ellipse([cx + 35, fy + 8, cx + 95, fy + 58], fill=(210, 155, 120, 255))
d.ellipse([cx + 55, fy + 18, cx + 100, fy + 52], fill=(200, 145, 110, 255))
# wrist going left-down
d.polygon(
    [(cx - 90, fy + 20), (cx - 40, fy + 70), (cx - 130, fy + 160), (cx - 175, fy + 120)],
    fill=(200, 140, 105, 255),
)

ov = ov.filter(ImageFilter.GaussianBlur(0.4))
out = Image.alpha_composite(base, ov).convert("RGB")
out.save(out_color, quality=95)

# canny-style: edges of cylinder + ring hand
canny = Image.new("L", im.size, 0)
cdw = ImageDraw.Draw(canny)
# cylinder outline
cdw.ellipse([cx - 42, y_tip - 16, cx + 42, y_tip + 24], outline=255, width=3)
cdw.line([(cx - 38, y_tip + 8), (cx - 52, y_base - 10)], fill=255, width=3)
cdw.line([(cx + 38, y_tip + 8), (cx + 52, y_base - 10)], fill=255, width=3)
cdw.ellipse([cx - 52, y_base - 18, cx + 52, y_base + 22], outline=255, width=3)
# ring of fingers around mid
cdw.ellipse([cx - 78, fy - 48, cx + 78, fy + 62], outline=255, width=4)
# knuckles
for kx, ky in knuckles:
    cdw.ellipse([kx - 22, ky - 20, kx + 22, ky + 26], outline=255, width=3)
# thumb
cdw.ellipse([cx + 40, fy + 10, cx + 98, fy + 56], outline=255, width=3)
# wrist
cdw.line([(cx - 70, fy + 40), (cx - 150, fy + 140)], fill=255, width=4)
canny.convert("RGB").save(out_canny)
print("saved", out_color, out_canny)
