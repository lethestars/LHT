import numpy as np
from PIL import Image

src = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\double_zhao_arms_up.jpg"
out = r"C:\Users\92982\.cursor\projects\c-Users-92982-Desktop-LHT\assets\double_zhao_height_fixed.jpg"

im = Image.open(src).convert("RGB")
arr = np.array(im)
h, w = arr.shape[:2]
print(h, w)

lift = int(h * 0.09)

yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")

cx = w / 2
sigma_x = w * 0.24
wx = np.exp(-((xx - cx) ** 2) / (2 * sigma_x ** 2))

y0, y1 = 0.10 * h, 0.60 * h
wy = np.clip((yy - y0) / (0.08 * h), 0, 1) * np.clip((y1 - yy) / (0.08 * h), 0, 1)

src_y = yy + lift * (wx * wy)
src_y = np.clip(src_y, 0, h - 1)

y0i = np.floor(src_y).astype(np.int32)
y1i = np.clip(y0i + 1, 0, h - 1)
ty = (src_y - y0i)[..., None]
x_idx = xx
out_arr = (arr[y0i, x_idx] * (1 - ty) + arr[y1i, x_idx] * ty).astype(np.uint8)

Image.fromarray(out_arr).save(out, quality=95)
print("saved", out, "lift", lift)
