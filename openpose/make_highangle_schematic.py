"""High-angle pose schematic: gray cylinder + clothes, no explicit anatomy."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

src = (
    r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets"
    r"\c__Users_92982_AppData_Roaming_Cursor_User_workspaceStorage_"
    r"-19c355fc_images_image-13b30c19-a84d-4da8-bf9c-f69a6f21090e.png"
)
out = r"C:\Users\92982\Desktop\LHT\openpose\36_highangle_schematic.jpg"
out_canny = r"C:\Users\92982\Desktop\LHT\openpose\36_highangle_schematic_canny.png"

im = Image.open(src).convert("RGBA")
w, h = im.size
ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)


def ellipse(box, fill, outline=None, width=2):
    d.ellipse(box, fill=fill, outline=outline, width=width if outline else 0)


# cover original dangling right arm (viewer's left)
cover = Image.new("RGBA", (w, h), (0, 0, 0, 0))
cd = ImageDraw.Draw(cover)
cd.polygon(
    [(40, 260), (160, 250), (190, 420), (150, 560), (40, 520), (20, 360)],
    fill=(248, 248, 250, 235),
)
cover = cover.filter(ImageFilter.GaussianBlur(8))
base = Image.alpha_composite(im, cover)

# --- white shirt bunched at neck / shoulders ---
# collar bunch
ellipse([210, 210, 400, 310], (245, 245, 248, 230), (210, 210, 215, 255), 2)
# left shoulder fabric (his right = viewer's left)
d.polygon(
    [(70, 250), (160, 230), (200, 280), (130, 340), (55, 310)],
    fill=(242, 242, 246, 220),
)
# right shoulder fabric (his left = viewer's right)
d.polygon(
    [(430, 250), (540, 270), (555, 360), (470, 400), (400, 300)],
    fill=(242, 242, 246, 220),
)

# --- blue jeans following thighs (not triangles) ---
jeans = (62, 110, 175, 215)
# hips / crotch
d.polygon(
    [
        (155, 528),
        (268, 542),
        (318, 542),
        (405, 555),
        (395, 640),
        (340, 635),
        (300, 628),
        (255, 628),
        (210, 632),
        (160, 620),
    ],
    fill=jeans,
)
# his right leg (viewer's left)
d.polygon(
    [
        (158, 618),
        (248, 630),
        (245, 760),
        (220, 860),
        (175, 858),
        (155, 740),
    ],
    fill=jeans,
)
# his left leg (viewer's right)
d.polygon(
    [
        (310, 630),
        (392, 638),
        (372, 780),
        (348, 875),
        (300, 872),
        (298, 740),
    ],
    fill=jeans,
)
# fly opening
d.polygon([(252, 545), (280, 545), (288, 618), (258, 616)], fill=(35, 50, 80, 230))
d.line([(205, 560), (195, 780)], fill=(40, 70, 120, 180), width=2)
d.line([(350, 575), (340, 800)], fill=(40, 70, 120, 180), width=2)

# --- gray cylinder standing from fly, toward camera (up the abs) ---
# stacked ellipses, hollow-looking rim, gray foam roller
cx = 278
y_tip, y_base = 488, 618
for y in range(y_tip, y_base, 3):
    t = (y - y_tip) / (y_base - y_tip)
    rr = int(22 + 8 * t)
    shade = int(168 + 28 * t)
    ellipse([cx - rr, y - 9, cx + rr, y + 16], (shade, shade + 2, shade + 6, 255))
# rim at tip
ellipse([cx - 22, y_tip - 14, cx + 22, y_tip + 18], (190, 194, 200, 255), (90, 95, 105, 255), 3)
# inner hole to read as HOLLOW tube
ellipse([cx - 10, y_tip - 6, cx + 10, y_tip + 8], (70, 74, 82, 255))
# base ring at fly
ellipse([cx - 30, y_base - 12, cx + 30, y_base + 16], None, (70, 75, 85, 255), 3)

# --- RIGHT FIST wrapping cylinder (viewer's left / his right) ---
skin = (214, 164, 128, 255)
skin_d = (190, 135, 100, 255)
fy, fx = 548, 278
# back of hand
ellipse([fx - 58, fy - 38, fx + 52, fy + 52], skin)
# four knuckles in FRONT
knuckles = [
    (fx - 30, fy - 8),
    (fx - 8, fy - 18),
    (fx + 14, fy - 16),
    (fx + 34, fy - 4),
]
for kx, ky in knuckles:
    ellipse([kx - 16, ky - 14, kx + 16, ky + 18], skin)
    ellipse([kx - 8, ky - 10, kx + 9, ky + 4], skin_d)
# thumb wrap from viewer's left
ellipse([fx - 62, fy + 2, fx - 18, fy + 36], skin)
ellipse([fx - 70, fy + 10, fx - 28, fy + 34], skin_d)
# wrist going to his right forearm
d.polygon(
    [(fx - 55, fy + 10), (fx - 20, fy + 40), (130, 500), (95, 455), (80, 400)],
    fill=skin,
)
# forearm
d.polygon([(78, 330), (125, 325), (150, 430), (95, 455), (70, 400)], fill=skin)

# --- LEFT ARM to LEFT pec pinch (viewer's right) ---
# upper arm from left shoulder
d.polygon([(470, 310), (545, 330), (560, 410), (500, 445), (455, 360)], fill=skin)
# forearm in
d.polygon([(500, 430), (555, 410), (430, 355), (390, 340), (375, 370), (490, 455)], fill=skin)
# pinch hand on left pec
nx, ny = 352, 345
ellipse([nx - 6, ny - 8, nx + 40, ny + 32], skin)  # palm
ellipse([nx - 18, ny - 20, nx + 10, ny + 8], skin)  # index
ellipse([nx - 8, ny + 8, nx + 20, ny + 30], skin)  # thumb
for fx2, fy2 in [(nx + 20, ny - 2), (nx + 30, ny + 8), (nx + 34, ny + 18)]:
    ellipse([fx2 - 10, fy2 - 8, fx2 + 10, fy2 + 11], skin)
# nipple target (small, non-graphic)
ellipse([nx - 5, ny - 5, nx + 6, ny + 6], (200, 140, 120, 255), (90, 50, 40, 255), 2)

out_im = Image.alpha_composite(base, ov).convert("RGB")

# labels
try:
    font = ImageFont.truetype("msyh.ttc", 22)
    font_s = ImageFont.truetype("msyh.ttc", 16)
except Exception:
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_s = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = font_s = None

draw = ImageDraw.Draw(out_im)
draw.rectangle([8, 6, 600, 78], fill=(255, 255, 255))
draw.text((16, 10), "HIGH ANGLE schematic  (gray tube = placeholder)", fill=(20, 20, 20), font=font)
draw.text((16, 38), "R fist FULL WRAP on tube     L pinch LEFT pec", fill=(30, 30, 30), font=font_s)
draw.text((16, 56), "white shirt pulled up     blue jeans unzipped", fill=(80, 80, 80), font=font_s)

out_im.save(out, quality=95)

# Canny-style: thin white hollow lines on black
canny = Image.new("RGB", (w, h), (0, 0, 0))
c = ImageDraw.Draw(canny)
# cylinder hollow
c.ellipse([cx - 22, y_tip - 14, cx + 22, y_tip + 18], outline=(255, 255, 255), width=3)
c.line([(cx - 20, y_tip + 8), (cx - 28, y_base - 4)], fill=(255, 255, 255), width=3)
c.line([(cx + 20, y_tip + 8), (cx + 28, y_base - 4)], fill=(255, 255, 255), width=3)
c.ellipse([cx - 30, y_base - 12, cx + 30, y_base + 16], outline=(255, 255, 255), width=3)
# fist ring
c.ellipse([fx - 48, fy - 32, fx + 46, fy + 42], outline=(255, 255, 255), width=3)
for kx, ky in knuckles:
    c.ellipse([kx - 14, ky - 12, kx + 14, ky + 16], outline=(255, 255, 255), width=2)
c.ellipse([fx - 62, fy + 2, fx - 18, fy + 36], outline=(255, 255, 255), width=2)
# right arm
c.line([(90, 320), (85, 400), (120, 460), (200, 530), (250, 548)], fill=(255, 255, 255), width=4)
# left arm
c.line([(510, 320), (548, 390), (520, 440), (430, 365), (360, 348)], fill=(255, 255, 255), width=4)
# pinch
c.ellipse([nx - 16, ny - 18, nx + 36, ny + 30], outline=(255, 255, 255), width=3)
canny.save(out_canny)
print("saved", out)
print("saved", out_canny)
