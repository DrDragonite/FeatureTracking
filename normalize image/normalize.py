# for i, rgb in enumerate(pix):
# 	rgb_sum = sum(rgb)
#
# 	normalized_r = int(rgb[0] / rgb_sum * 255)
# 	normalized_g = int(rgb[1] / rgb_sum * 255)
# 	normalized_b = int(rgb[2] / rgb_sum * 255)
#
# 	pix[i] = (normalized_r, normalized_g, normalized_b)

def normalize(pixels: list) -> list:
	"""Returns a list of normalized RGB values from list of RGB tuples."""
	return [(int(rgb[0] / sum(rgb) * 255), int(rgb[1] / sum(rgb) * 255), int(rgb[2] / sum(rgb) * 255)) for rgb in list(pixels)]
