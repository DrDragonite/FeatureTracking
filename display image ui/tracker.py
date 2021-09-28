# globals
NUMBER = (int, float)
MODES  = ("TOPLEFT", "CENTER")

class Tracker:
	def __init__(self, x: float, y: float, width: float, height: float, *, bg_margin: float = 10, mode: str = "CENTER") -> None:
		self.set(x=x, y=y, width=width, height=height, bg_margin=bg_margin, mode=mode)
		self.fg_rect = None
		self.bg_rect = None

	def set(self, x=None, y=None, width=None, height=None, bg_margin=None, mode=None) -> None:
		self.x         = x         if isinstance(x, NUMBER)         else self.x
		self.y         = y         if isinstance(y, NUMBER)         else self.y
		self.width     = width     if isinstance(width, NUMBER)     else self.width
		self.height    = height    if isinstance(height, NUMBER)    else self.height
		self.bg_margin = bg_margin if isinstance(bg_margin, NUMBER) else self.bg_margin
		self.bg_width  = self.width  + self.bg_margin
		self.bg_height = self.height + self.bg_margin
		if mode and (not isinstance(mode, str) or not mode.upper() in MODES):
			raise Exception("Invalid mode")
		self.mode = mode if mode else self.mode

	def tk_draw(self, canvas):
		if not self.fg_rect: self.fg_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#00ff00", fill=None)
		if not self.bg_rect: self.bg_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#00ff00", fill=None)
		x1, y1, x2, y2 = self.fg_coords()
		canvas.coords(self.fg_rect, x1, y1, x2, y2)
		x1, y1, x2, y2 = self.bg_coords()
		canvas.coords(self.bg_rect, x1, y1, x2, y2)

	def tk_undraw(self, canvas):
		if self.fg_rect: canvas.delete(self.fg_rect)
		if self.bg_rect: canvas.delete(self.bg_rect)

	def fg_coords(self):
		self.set()
		# calculate offsets
		x_off = 0
		y_off = 0
		if self.mode == "CENTER":
			x_off = self.width / 2
			y_off = self.height / 2

		# calculate coordinates with offset applied
		x1_o = self.x - x_off
		y1_o = self.y - y_off
		x2_o = x1_o + self.width
		y2_o = y1_o + self.height

		# return the coordinates
		return (x1_o, y1_o, x2_o, y2_o)

	def bg_coords(self):
		self.set()
		# calculate offsets
		x_off = 0
		y_off = 0
		if self.mode == "CENTER":
			x_off = self.bg_width
			y_off = self.bg_height

		# calculate coordinates with offset applied
		x1_o = self.x - self.bg_margin - x_off
		y1_o = self.y - self.bg_margin - y_off
		x2_o = x1_o + self.bg_width  + self.bg_margin
		y2_o = y1_o + self.bg_height + self.bg_margin

		# return the coordinates
		return (x1_o, y1_o, x2_o, y2_o)

	def get_fg(self, pixels: list, image_width: int, image_height: int) -> list:
		from util import constrain

		foreground: list = []

		# calculate border-constrained coordinates
		x1, y1, x2, y2 = self.fg_coords()
		x1_c = constrain(x1, 0, image_width)
		y1_c = constrain(y1, 0, image_height)
		x2_c = constrain(x2, 0, image_width)
		y2_c = constrain(y2, 0, image_height)

		for y in range(y1_c, y2_c):
			# get the edges of a horizontal "strip" of the foreground
			i_start = x1_c + y * image_width
			i_end   = x2_c + y * image_width

			# add said strip to the foreground array
			foreground.append(pixels[int(i_start):int(i_end)])

		# return the foreground array
		return foreground

	def get_bg(self, pixels: list, image_width: int, image_height: int) -> list:
		from util import constrain

		background: list = []

		# calculate border-constrained coordinates
		x1, y1, x2, y2 = self.bg_coords()
		x1_c = constrain(x1, 0, image_width)
		y1_c = constrain(y1, 0, image_height)
		x2_c = constrain(x2, 0, image_width)
		y2_c = constrain(y2, 0, image_height)

		for y in range(y1_c, y2_c):
			# get the edges of a horizontal "strip" of the background
			i_start = x1_c + y * image_width
			i_end   = x2_c + y * image_width

			# add said strip to the background array
			background.append(pixels[int(i_start):int(i_end)])

		# return the background array
		return background

	def is_fg(self, x, y):
		return x > self.bg_margin and x < self.bg_width - self.bg_margin * 2 and y > self.bg_margin and y < self.bg_height - self.bg_margin * 2
	
	def is_bg(self, x, y):
		return not self.is_fg(x, y)

	def __str__(self) -> str:
		self.set()
		return "Tracker(x={}, y={}, w={}, h={}, bw={}, bh={}, bm={}, cm={})".format(self.x, self.y, self.width, self.height, self.bg_width, self.bg_height, self.bg_margin, self.mode)
