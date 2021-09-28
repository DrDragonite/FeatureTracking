def constrain(value: float, _min: float, _max: float) -> float:
	"""Returns given value constrained between _min and _max."""
	return min(max(value, _min), _max)

def constrained(value: float, _min: float, _max: float) -> bool:
	"""Returns whether the given value is constrained betwen _min and _max."""
	return value >= _min and value <= _max

def frequency(value_arr: list, value: int) -> float:
	"""Returns frequency of values within the given array."""
	return value_arr.count(value)/len(value_arr)

def round(value: float) -> int:
	"""Round a float to an integer"""
	return int(value + 0.5)

def get_coord(index: int, width: int, height: int) -> tuple:
	"""Get X and Y coordinates from a 1D index"""
	return (index / height, index % height)

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
	return Counter(values).most_common(1)[0]


def normalize_rgb(pixels: list) -> list:
	"""Returns a list of normalized RGB values from list of RGB tuples."""
	return [(int(rgb[0] / sum(rgb) * 255), int(rgb[1] / sum(rgb) * 255), int(rgb[2] / sum(rgb) * 255)) for rgb in list(pixels)]

def log_likelihood_ratio(fg: list, bg: list) -> float:
	from math import log2

	# tiny_number = 0.0001
	# fraction = max(fg_f, tiny_number) / max(fg_f, tiny_number)
	# result1 = log2(fraction)
	# result  = max(-1, min(result1))

	return max(-1, min(1, log2(max(most_common(fg), 0.0001) / max(most_common(bg), 0.0001))))
	

def likelihood_image(image, tracker, mode = "R", precision = 5) -> list:
	# get the image pixel and size data
	pix = list(image.convert("RGB").getdata())
	w = image.width 
	h = image.height

	# get the tracked pixels in RGB tuples
	fg_p = tracker.get_fg(pix, w, h)
	bg_p = tracker.get_bg(pix, w, h)

	# channel count
	cc = 1

	# foreground and background value lists
	fg = [0] * len(fg_p)
	bg = [0] * len(bg_p)

	j = 0
	# add and mix in the desired values
	for i, rgb in enumerate(bg_p):
		x, y = get_coord(i, w, h)
		is_fg = tracker.is_fg(x, y)

		# unchanged pixel values (RGB)
		if "R" in mode:
			fg[j] = fg[j] + int((rgb[0] - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[0] - bg[i]) / cc)
			cc += 1
		if "G" in mode:
			fg[j] = fg[j] + int((rgb[1] - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[1] - bg[i]) / cc)
			cc += 1
		if "B" in mode:
			fg[j] = fg[j] + int((rgb[2] - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[2] - bg[i]) / cc)
			cc += 1
	
		# normalized pixel values (rgb)
		if "r" in mode:
			fg[j] = fg[j] + int((rgb[0] / sum(rgb) * 255 - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[0] / sum(rgb) * 255 - bg[i]) / cc)
			cc += 1
		if "g" in mode:
			fg[j] = fg[j] + int((rgb[1] / sum(rgb) * 255 - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[1] / sum(rgb) * 255 - bg[i]) / cc)
			cc += 1
		if "b" in mode:
			fg[j] = fg[j] + int((rgb[2] / sum(rgb) * 255 - fg[j]) / cc * is_fg)
			bg[i] = bg[i] + int((rgb[2] / sum(rgb) * 255 - bg[i]) / cc)
			cc += 1

		fg[j] = map_range_int(fg[j], 0, 255, 0, pow(2, precision))
		bg[i] = map_range_int(bg[i], 0, 255, 0, pow(2, precision))
		j += is_fg
		
	
	rt = log_likelihood_ratio(fg, bg)

	print(rt)

