from PIL import Image
from normalize import normalize

root = __file__[:__file__.rfind("/")+1]

# load image
img = Image.open(f"{root}img/src.png").convert("RGB")

#load pixels
pix = list(img.getdata())

# create output image image
out_img = Image.new(img.mode, img.size)
out_img.putdata(normalize(pix))

# save output image
out_img.save(f"{root}img/normalized.png")
