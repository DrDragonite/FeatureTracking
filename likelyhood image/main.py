from posixpath import realpath
from PIL import Image
from tracker import Tracker

__folder__ = __file__[:__file__.rfind("/")+1]

img = Image.open(__folder__+"img/src.png").convert("RGB")
pix = list(img.getdata())

tracker = Tracker(0, 0, 0, 0)
print(tracker)
