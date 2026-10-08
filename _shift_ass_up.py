from PIL import Image, ImageDraw, ImageFilter, ImageChops

src = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\c__Users_92982_AppData_Roaming_Cursor_User_workspaceStorage_-19c355fc_images_double_zhao_from_carry_ref-94f65419-f221-4519-b458-9b55c9c3691c.jpg"
out = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\double_zhao_ass_to_blue.jpg"

im = Image.open(src).convert("RGBA")
w, h = im.size
print("size", w, h)

# shift center hips up ~9% of height (red nadir -> blue line)
shift = int(h * 0.09)

# region covering 骚零 body + inner thighs of the lift
box = (int(w * 0.18), int(h * 0.08), int(w * 0.82), int(h * 0.58))
crop = im.crop(box)
cw, ch = crop.size

# feathered mask: keep center figure, fade edges
mask = Image.new("L", (cw, ch), 0)
md = ImageDraw.Draw(mask)
md.ellipse(
    [int(cw * 0.12), int(ch * 0.02), int(cw * 0.88), int(ch * 0.98)],
    fill=255,
)
mask = mask.filter(ImageFilter.GaussianBlur(18))

layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
# paste crop higher
ny = box[1] - shift
layer.paste(crop, (box[0], ny))
# apply mask at new position
full_mask = Image.new("L", im.size, 0)
full_mask.paste(mask, (box[0], ny))
layer.putalpha(full_mask)

# fill the hole left below with a stretched patch of the door between legs
fill_y0 = box[1] + int(ch * 0.55)
fill_y1 = min(h, box[3] + 20)
fill_x0, fill_x1 = int(w * 0.38), int(w * 0.62)
door = im.crop((fill_x0, int(h * 0.62), fill_x1, int(h * 0.82))).resize(
    (fill_x1 - fill_x0, fill_y1 - fill_y0)
)
base = im.copy()
base.paste(door, (fill_x0, fill_y0))

out_im = Image.alpha_composite(base, layer).convert("RGB")
out_im.save(out, quality=95)
print("saved", out, "shift", shift)
