class ValueRange():
	def __init__(self) -> None:
		self.min = None
		self.max = None
	
	def record(self, val: float) -> None:
		if self.min is None: self.min = val
		if self.max is None: self.max = val
		self.max = max(self.max, val)
		self.min = min(self.min, val)
	
	def reset(self):
		self.__init__()

	def __str__(self) -> str:
		return "(%.2f - %.2f)" % (self.min, self.max)
	
	def __repr__(self) -> str:
		return "ValueRange(min: %.2f max: %.2f)" % (self.min, self.max)

def constrain(value: float, _min: float, _max: float) -> float:
	"""Returns given value constrained between _min and _max."""
	return min(max(value, _min), _max)

def constrained(value: float, _min: float, _max: float) -> bool:
	"""Returns whether the given value is constrained betwen _min and _max."""
	return value >= _min and value <= _max

def frequency(arr: list, value: int) -> float:
	"""Returns frequency of values within the given array."""
	return arr.count(value)/len(arr)

def count_frequency(arr: list, value: int) -> float:
	"""Returns frequency of values within the given count array."""
	count = sum(arr)
	if not count: return 0
	return arr[value]/count

def round(value: float) -> int:
	"""Round a float to an integer"""
	return int(value + 0.5)

def index_to_coords(index: int, width: int, height: int) -> tuple:
	"""Get X and Y coordinates from a 1D index"""
	return (index % width, index // width)

def coords_to_index(x: int, y: int, width: int) -> tuple:
	"""Get 1D index coordinates x and y."""
	return x + y * width

def map_range(values: list, input_start: float, input_end: float, output_start: float, output_end: float) -> list:
	"""Returns given values mapped from input range to output range."""
	if not isinstance(values, list): values = [values]
	return [output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start) for value in values]

def map_range_int(values: list, input_start: float, input_end: float, output_start: float, output_end: float) -> list:
	"""Returns given values mapped from input range to output range."""
	if not isinstance(values, list): values = [values]
	return [round(output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start)) for value in values]

# bleh
def histogram(values: list, b_count: int, range_from: int, range_to: int) -> list:
	"""Returns a histogram of given values."""
	from collections import Counter

	histogram = Counter(map_range_int(values, range_from, range_to, 0, b_count))
	return [histogram[x] for x in range(1, b_count+1)]

def most_common(values: list):
	"""Returns the most common element from a list of elements."""
	from collections import Counter
	return Counter(values).most_common(1)[0][0]

def normalize_rgb(pixel: tuple) -> list:
	"""Returns normalized RGB value."""
	return (int(pixel[0] / sum(pixel) * 255), int(pixel[1] / sum(pixel) * 255), int(pixel[2] / sum(pixel) * 255))

def image_to_array(img):
	from numpy import flipud, rot90, array
	#return flipud(rot90(array(img.convert("RGB")), 1)).astype(int)
	return array(img.convert("RGB")).astype(int)

def array_to_image(arr, mode="L"):
	from PIL import Image
	from numpy import flipud, rot90, uint8
	#return Image.fromarray(flipud(rot90(arr, 1)).astype(uint8), mode)
	return Image.fromarray(arr.astype(uint8), mode)

def integral(pix):
	"""Returns an integral image from 2-D pixel array."""
	from numpy import zeros
	itg = zeros((pix.shape[0]+1, pix.shape[1]+1))
	itg[1:, 1:] = pix.cumsum(0).cumsum(1)
	return itg.astype(int)

def integral_get_area(itg, x0, y0, x1, y1):
	x0, y0 = (max(x0, 0), max(y0, 0))
	_A = itg[x0-1, y0-1]
	_B = itg[x1,   y0-1]
	_C = itg[x1,   y1]
	_D = itg[x0-1, y1]
	return int(_C - _B - _D + _A)

def integral_get_point(itg, x, y):
	return integral_get_area(itg, x-1, y-1, x, y)

def any_eq(str1, str2):
	"""Return whether every character in str1 is present in str2."""
	return sum([ch in str2 for ch in list(str1)]) > 0

def log_likelihood_ratio_old(fg: list, bg: list, i: int) -> float:
	from math import log10

	# tiny_number = 0.0001
	# fg_f = frequency(fg, i)
	# bg_f = frequency(bg, i)
	# fraction = max(fg_f, tiny_number) / max(bg_f, tiny_number)
	# result1 = log2(fraction)
	# result  = max(-1, min(1, result1))

	#print(frequency(fg, i), frequency(bg, i), max(frequency(fg, i), 0.0001) / max(frequency(bg, i), 0.0001))
	return max(-1, min(1, log10(max(frequency(fg, i), 0.0001) / max(frequency(bg, i), 0.0001))))

def likelihood_image_old(image, tracker, mode = "RGB", precision = 64) -> list:
	from PIL import Image

	# constrain the precision
	precision = constrain(precision, 1, 255)

	# load image data
	pix = list(image.convert("RGB").getdata())
	w = image.width 
	h = image.height

	# shorten tracker variables
	tx = tracker.x
	ty = tracker.y
	tw = tracker.width
	th = tracker.height
	bw = tracker.bg_width
	bh = tracker.bg_height
	bm = tracker.bg_margin

	# prepare the getter function
	def R(rgb): return int(rgb[0])
	def G(rgb): return int(rgb[1])
	def B(rgb): return int(rgb[2])
	def r(rgb): return int(rgb[0]/sum(rgb)*255)
	def g(rgb): return int(rgb[1]/sum(rgb)*255)
	def b(rgb): return int(rgb[2]/sum(rgb)*255)
	def avg(*val): return sum(val)//len(val)
	def get(x, loc):
		loc["x"] = x
		return eval("avg("+",".join([x+"(x)" for x in list(mode)])+")", loc)

	# prepare arrays and set globals
	img = ["0"] * (w * h)
	fg  = ["0"] * (tw * th)
	bg  = ["0"] * (bw * bh - tw * th)
	fg_c = 0
	bg_c = 0
	for i, rgb in enumerate(pix):
		# differentiate between foreground and background
		x, y  = index_to_coords(i, w, h)
		is_fg = tracker.is_fg(x - tx, y - ty)
		is_bg = tracker.is_bg(x - tx, y - ty)
		# get the pixel value based on the mode
		val = get(rgb, locals())

		# limit the amount of values to precision
		val = int(val / 255 * precision)

		# set the values
		img[i] = val
		if   is_fg: fg[fg_c] = val; fg_c += 1
		elif is_bg: bg[bg_c] = val; bg_c += 1

	# with open("/home/student11/Python/Michal Kostrhun/feature tracking/display image ui/arr.txt", "w") as file:
	# 	file.write(str(img))
	# return

	# handle clipping out of image
	fg = list(filter(lambda x: x != "0", fg))
	bg = list(filter(lambda x: x != "0", bg))
	if not fg or not bg: return
	
	# calculate the ratios
	ratios = [log_likelihood_ratio(fg, bg, x) for x in range(precision+1)]

	# apply the ratios to the image
	l_img = [(ratios[x] + 1) * 128 for x in img]

	# display the image
	l_image = Image.new("L", (w, h))
	l_image.putdata(l_img)
	return l_image

def log_likelihood_ratio(fg: list, bg: list, i: int) -> float:
	from math import log10
	return max(-1, min(1, log10(max(count_frequency(fg, i), 0.00001) / max(count_frequency(bg, i), 0.00001))))

def likelihood_image(image, tracker, mode = "RGB", color_count = 64):
	import numpy as np

	# constrain the color count
	color_count = constrain(color_count, 1, 255)

	# load image data
	img = image_to_array(image)
	w = image.width
	h = image.height

	# combine selected RGB pixels into single desired value
	if not any_eq("RGB", mode.upper()): return
	selector = ["R" in mode, "G" in mode, "B" in mode]
	img = (img[..., selector].mean(2) / 255 * color_count).astype(int)

	# shorten tracker variables
	tx = tracker.x
	ty = tracker.y
	tw = tracker.width
	th = tracker.height
	bm = tracker.bg_margin

	# initiate fg and bg arrays
	fg = np.zeros_like(img)
	bg = np.zeros_like(img)

	# compute the fg and bg masks
	fg[ty:ty+th, tx:tx+tw] = 1
	bg[ty-bm:ty+tw+bm, tx-bm:tx+tw+bm] = 1
	bg = bg - fg

	fg_count = [0] * (color_count + 1)
	bg_count = [0] * (color_count + 1)
	for i in range(color_count + 1):
		# only choose the values we're currently working with
		val = img == i

		# apply fg and bg masks and count the values
		fg_count[i] = (val * fg).sum()
		bg_count[i] = (val * bg).sum()

	# calculate the ratios
	ratios = [log_likelihood_ratio(fg_count, bg_count, x) for x in range(color_count+1)]

	# apply the ratios to the image
	for i in range(color_count + 1):
		img[img == i] = int((ratios[i] + 1) * 127) + 1

	# return the image
	return array_to_image(img)
