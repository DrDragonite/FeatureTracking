# globals
NUMBER = (int, float)
MODES  = ("TOPLEFT", "CENTER")

class Tracker:
	def __init__(self, x: float, y: float, width: float, height: float, *, bg_margin: float = 10, mode: str = "CENTER") -> None:
		self.set(x=x, y=y, width=width, height=height, bg_margin=bg_margin, mode=mode)
		self.i_fg_rect = None
		self.i_bg_rect = None

	def set(self, x=None, y=None, width=None, height=None, bg_margin=None, mode=None) -> None:
		self.x         = x         if isinstance(x, NUMBER)         else self.x
		self.y         = y         if isinstance(y, NUMBER)         else self.y
		self.width     = width     if isinstance(width, NUMBER)     else self.width
		self.height    = height    if isinstance(height, NUMBER)    else self.height
		self.bg_margin = bg_margin if isinstance(bg_margin, NUMBER) else self.bg_margin
		self.bg_width  = self.width  + self.bg_margin * 2
		self.bg_height = self.height + self.bg_margin * 2
		if mode and (not isinstance(mode, str) or not mode.upper() in MODES):
			raise Exception("Invalid mode")
		self.mode = mode if mode else self.mode

	def offset(self, x, y):
		return type(self)(self.x - x, self.y - y, self.width, self.height, bg_margin=self.bg_margin, mode=self.mode)

	def tk_draw(self, canvas):
		if not self.i_fg_rect: self.i_fg_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#00ff00", fill=None)
		if not self.i_bg_rect: self.i_bg_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#00ff00", fill=None)
		x1, y1, x2, y2 = self.fg_coords()
		canvas.coords(self.i_fg_rect, x1, y1, x2, y2)
		x1, y1, x2, y2 = self.bg_coords()
		canvas.coords(self.i_bg_rect, x1, y1, x2, y2)

	def tk_undraw(self, canvas):
		if self.i_fg_rect: canvas.delete(self.i_fg_rect)
		if self.i_bg_rect: canvas.delete(self.i_bg_rect)

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
			x_off = self.bg_width  // 2
			y_off = self.bg_height // 2

		# calculate coordinates with offset applied
		x1_o = self.x - self.bg_margin - x_off
		y1_o = self.y - self.bg_margin - y_off
		x2_o = x1_o + self.bg_width
		y2_o = y1_o + self.bg_height

		# return the coordinates
		return (x1_o, y1_o, x2_o, y2_o)

	def get_fg(self, pixels: list, image_width: int, image_height: int) -> list:
		from util import constrain

		foreground: list = []

		# calculate border-constrained coordinates
		x1, y1, x2, y2 = self.fg_coords()
		x1_c = int(constrain(x1, 0, image_width))
		y1_c = int(constrain(y1, 0, image_height))
		x2_c = int(constrain(x2, 0, image_width))
		y2_c = int(constrain(y2, 0, image_height))

		for y in range(y1_c, y2_c):
			# get the edges of a horizontal "strip" of the foreground
			i_start = x1_c + y * image_width
			i_end   = x2_c + y * image_width

			# add said strip to the foreground array
			foreground += pixels[int(i_start):int(i_end)]

		# return the foreground array
		return foreground

	def get_bg(self, pixels: list, image_width: int, image_height: int) -> list:
		from util import constrain

		background: list = []

		# calculate border-constrained coordinates
		x1, y1, x2, y2 = self.bg_coords()
		x1_c = int(constrain(x1, 0, image_width))
		y1_c = int(constrain(y1, 0, image_height))
		x2_c = int(constrain(x2, 0, image_width))
		y2_c = int(constrain(y2, 0, image_height))

		for y in range(y1_c, y2_c):
			# get the edges of a horizontal "strip" of the background
			i_start = x1_c + y * image_width
			i_end   = x2_c + y * image_width

			# add said strip to the background array
			background += pixels[int(i_start):int(i_end)]

		# return the background array
		return background

	def is_fg(self, x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height
	
	def is_bg(self, x, y):
		#return x > -self.bg_margin and x < self.bg_width and y > -self.bg_margin and y < self.bg_height
		return x >= -self.bg_margin and x < self.width + self.bg_margin and y >= -self.bg_margin and y < self.height + self.bg_margin

	def __str__(self) -> str:
		self.set()
		return "Tracker(x={}, y={}, w={}, h={}, bw={}, bh={}, bm={}, m={})".format(self.x, self.y, self.width, self.height, self.bg_width, self.bg_height, self.bg_margin, self.mode)
