from math import exp
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

class Console(ScrolledText):
	def __init__(self, *args, **kwargs) -> None:
		import sys
		super().__init__(*args, **kwargs)
		self.ch_count = 0

		class ConsoleManager:
			def __init__(self, widget: Text, old_stdout: sys.stdout):
				self.console = widget
				self.old_stdout = old_stdout
				
			def write(self, string):
				from datetime import datetime

				if self.console.ch_count > 1000:
					self.console.ch_count -= 500
					self.console.delete("1.0", "499.0")

				# write to default console
				self.old_stdout.write(string)

				# write to text widget
				self.console.insert('end', string)
				self.console.see('end')
				self.console.ch_count += 1

			def flush(*a, **kw):
				pass

		sys.stdout = ConsoleManager(self, sys.stdout)

class InfoText(Label):
	def __init__(self, *args, **kwargs) -> None:
		self.text = StringVar()
		super().__init__(textvariable=self.text, *args, **kwargs)
		self.infodict = {}

	def update_info(self):
		arr = []
		for key, value in self.infodict.items():
			arr.append(f"{key}: {value}")
		self.text.set(", ".join(arr))
		self.update()
	
	def set(self, **kwargs):
		for key, value in kwargs.items():
			self.infodict[key] = value
		self.update_info()

class Selection:
	def __init__(self, x1, y1, x2=None, y2=None, w=None, h=None) -> None:
		self.x1, self.y1, self.x2, self.y2, w, h = (0,0,0,0,0,0)
		self.set(x1=x1, y1=y1, x2=x2, y2=y2, w=w, h=h)

	def set(self, x1=None, y1=None, x2=None, y2=None, w=None, h=None):
		self.x1 = x1 if not x1 is None else self.x1
		self.y1 = y1 if not y1 is None else self.y1
		self.x2 = (self.x1 + w if not w is None else (x2 if not x2 is None else self.x2))
		self.y2 = (self.y1 + h if not h is None else (y2 if not y2 is None else self.y2))
		self.w  = abs(self.x1 - self.x2)
		self.h  = abs(self.y1 - self.y2)

class SelectionManager:
	def __init__(self) -> None:
		self.shape_id = None
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0

	def create(self, canvas: Canvas, x: int, y: int, **kwargs) -> None:
		self.shape_id = canvas.create_rectangle(x, y, x, y, **kwargs)
		self.x1, self.y1, self.x2, self.y2 = (x, y, x, y)
	
	def adjust(self, canvas: Canvas, x: int, y: int) -> None:
		if not self.shape_id: return
		self.x2, self.y2 = (x, y)
		rx1 = self.x1 if self.x1 < self.x2 else self.x2
		ry1 = self.y1 if self.y1 < self.y2 else self.y2
		rx2 = self.x1 if self.x1 > self.x2 else self.x2
		ry2 = self.y1 if self.y1 > self.y2 else self.y2
		canvas.coords(self.shape_id, rx1, ry1, rx2, ry2)
	
	def delete(self, canvas: Canvas) -> tuple:
		canvas.delete(self.shape_id)
		x1 = self.x1 if self.x1 < self.x2 else self.x2
		y1 = self.y1 if self.y1 < self.y2 else self.y2
		x2 = self.x1 if self.x1 > self.x2 else self.x2
		y2 = self.y1 if self.y1 > self.y2 else self.y2
		coords = (x1, y1, x2, y2)
		self.__init__()
		return coords

class Switch:
	def __init__(self) -> None:
		self.state = False
		self.onchange = None

	def __len__(self) -> bool:
		return self.state

	def __repr__(self) -> str:
		return str(self.state)
	
	def __eq__(self, other) -> bool:
		return self.state == other

	def set(self, state: bool):
		if self.state != bool(state):
			if self.onchange: self.onchange(bool(state))
		self.state = bool(state)
	
	def toggle(self):
		self.state = not self.state
		if self.onchange: self.onchange(self.state)

class TransformSwitch:
	def __init__(self) -> None:
		self.state = "none"
		self.states = ["move", "topleft", "top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "none"]
		self.onchange = None

	def __repr__(self) -> str:
		return str(self.state)

	def __eq__(self, other) -> bool:
		return self.state == str(other).lower()
	
	def set(self, state: str):
		state = str(state).lower()
		if not state in self.states: return 
		if self.state != state:
			if self.onchange: self.onchange(state)
		self.state = state
	
	def to_cursor(self):
		return ["fleur", "size_nw_se", "size_ns", "size_ne_sw", "size_we", "size_nw_se", "size_ns", "size_ne_sw", "size_we", ""][self.states.index(self.state)]

class TransformManager:
	def __init__(self) -> None:
		self.show_handles  = True
		self.fixed_radtio  = False
		self.center_marker = None
		self.main_rect     = None
		self.handles       = None
		self.x1            = 0
		self.y1            = 0
		self.x2            = 0
		self.y2            = 0
		self.ox            = 0
		self.oy            = 0
	
	def create(self, canvas: Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
		self.x1, self.y1, self.x2, self.y2 = (x1, y1, x2, y2)
		self.main_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#558ef0", fill=None)
		self.center_marker = [canvas.create_line(0, 0, 0, 0, fill="#558ef0") for i in range(2)]
		self.handles = [canvas.create_rectangle(0, 0, 0, 0, outline="#558ef0", fill="#ffffff") if i != 4 else None for i in range(9)]
		self.update(canvas)

	def update(self, canvas: Canvas) -> None:
		"""Update the objects on the canvas."""
		if not self.center_marker or not self.main_rect or not self.handles:
			raise Exception("Please call 'create' function first")
		rx1 = self.x1 if self.x1 < self.x2 else self.x2
		ry1 = self.y1 if self.y1 < self.y2 else self.y2
		rx2 = self.x1 if self.x1 > self.x2 else self.x2
		ry2 = self.y1 if self.y1 > self.y2 else self.y2
		canvas.coords(self.main_rect, rx1, ry1, rx2, ry2)

		cx = round(rx1+(rx2-rx1)/2)
		cy = round(ry1+(ry2-ry1)/2)
		canvas.coords(self.center_marker[0], cx-3, cy,   cx+4, cy)
		canvas.coords(self.center_marker[1], cx,   cy-3, cx,   cy+4)

		for i in range(9):
			if i == 4: continue
			# if show_handles is false, hide the handles
			if self.show_handles: canvas.itemconfig(self.handles[i], state="normal")
			else: canvas.itemconfig(self.handles[i], state="hidden"); continue
			# if fixed_ratio is true, hide the in-between handles
			if self.fixed_radtio and not (i+1) % 2: canvas.itemconfig(self.handles[i], state="hidden"); continue
			else: canvas.itemconfig(self.handles[i], state="normal")

			x = int(i % 3)
			y = int(i / 3)
			#w = 6 + (1 * ((i+1) % 2))  # make corners bigger
			w = 7
			hx = rx1 + x * abs(rx2-rx1)/2
			hy = ry1 + y * abs(ry2-ry1)/2
			canvas.coords(self.handles[i], hx - w/2, hy - w/2, hx + w/2, hy + w/2)
	
	def delete(self, canvas: Canvas) -> None:
		"""Delete and reset the transform manager."""
		if self.main_rect: canvas.delete(self.main_rect)
		for i in range(9):
			if i < 2  and self.center_marker: canvas.delete(self.center_marker[i])
			if i != 4 and self.handles: canvas.delete(self.handles[i])
		self.__init__()
	
	def adjust(self, canvas: Canvas, mode: TransformSwitch, x: int, y: int) -> None:
		if "top" in mode.state:
			self.y1 = y
		if "right" in mode.state:
			self.x2 = x
		if "bottom" in mode.state:
			self.y2 = y
		if "left" in mode.state:
			self.x1 = x
		if "move" in mode.state:
			w  = self.x2 - self.x1
			h  = self.y2 - self.y1
			self.x1 = x - self.ox
			self.y1 = y - self.oy
			self.x2 = self.x1 + w
			self.y2 = self.y1 + h
		self.update(canvas)

	def set_offset(self, x, y) -> None:
		"""Set the offset for movement."""
		self.ox = x - self.x1
		self.oy = y - self.y1

	def reset_coords(self) -> None:
		"""Order coordinates properly, making sure (x1, y1) is the top left corner."""
		if self.x1 > self.x2:
			self.x2 = self.x2 + self.x1
			self.x1 = self.x2 - self.x1
			self.x2 = self.x2 - self.x1
		if self.y1 > self.y2:
			self.y2 = self.y2 + self.y1
			self.y1 = self.y2 - self.y1
			self.y2 = self.y2 - self.y1

	def coords(self) -> tuple:
		"""Get the transformation coordinates: (x1, y1, x2, y2)"""
		self.reset_coords()
		return (self.x1, self.y1, self.x2, self.y2)

class ChooseImage:
	def __init__(self) -> None:
		self.image = 0
	
	def __new__(self) -> PhotoImage:
		from PIL import Image, ImageTk
		from tkinter import filedialog
		filepath = filedialog.askopenfilename(initialdir=folder+"src", title="Load an image", filetypes=(("Image files", ("*.png", "*.gif*", "*.jpg", "*.jpeg")), ("All files", ("*.*"))))
		if not filepath: return
		self.image = image = ImageTk.PhotoImage(Image.open(filepath))
		return image

folder = __file__[:__file__.rfind("/")+1]

class UI(Frame):
	def __init__(self, root: Tk, *args, **kwargs):
		Frame.__init__(self, root, *args, **kwargs)
		self.pack(fill=BOTH, expand=1, padx=2, pady=2)
		self.root = root

		self.root.title("Image GUI")
		self.root.geometry("800x480")
		self.root.resizable(0, 0)
		#root.wm_attributes("-toolwindow", "true")

		self.transform_state = Switch()
		self.transform_mode = TransformSwitch()
		self.marker_state = Switch()
		self.m_movement = 0
		self.create_ui()

	def create_ui(self):
		self.footer = Frame(self, relief="flat")
		self.footer.pack(side="bottom", fill="x")
		
		self.sideframe = Frame(self, relief="groove", borderwidth=2, pady=10)
		self.sideframe.pack(side="left", fill="y", ipadx=10)

		self.mainframe = Frame(self, relief="flat")
		self.mainframe.pack(side="right", fill="both", expand=1)

		self.displayframe = Frame(self.mainframe, relief="groove", borderwidth=2)
		self.displayframe.pack(side="top", fill="both", expand=1, anchor="n")

		self.console = Console(self.mainframe, bg="#0f0f0f", fg="white", height=6)
		self.console.pack(side="top", fill="x")
		self.console.config(blockcursor=1, selectbackground="#9a9a9a", insertbackground="#9a9a9a", takefocus=0)
		self.console.bind("<Key>", lambda x: "break")
		self.console.bind("<FocusIn>", lambda x: "break")

		self.setup_canvas(self.displayframe)
		self.i_coords = InfoText(self.footer)
		self.i_coords.pack(anchor="nw")
		self.i_coords.set(x=0, y=0)

		self.marker_state.onchange = self.change_marker_button_state
		self.draw_marker_button = Button(self.sideframe, text="Draw marker", command=self.marker_state.toggle)
		self.draw_marker_button.pack(side="top", pady=5)

		self.load_image_button = Button(self.sideframe, text="Load image", command=self.load_image_to_canvas)
		self.load_image_button.pack(side="top", pady=5)

	def remove_focus(self):
		"""Remove focus from a text area."""
		self.root.focus_set()

	def load_image_to_canvas(self):
		img = ChooseImage() # needs to be a class because it doesn't work otherwise
		if not img: return
		self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=img, anchor="center")

	def change_marker_button_state(self, state):
		# change button style
		if state: self.draw_marker_button.config(fg="red", relief="sunken")
		else: self.draw_marker_button.config(fg="black", relief="raised")

	def setup_canvas(self, parent: Widget):
		def coords(event):
			"""Get X and Y coordinates from a mouse event."""
			return (int(event.x), int(event.y))
		
		def point_intersects_square_xyw(x, y, square_x, square_y, square_rad):
			"""Return whether a point (x, y) intersects with a square centered at (square_x, square_y) with size (2 * square_rad)"""
			return x >= square_x - square_rad and x <= square_x + square_rad and y >= square_y - square_rad and y <= square_y + square_rad

		def point_intersects_rect_xyxy(x, y, rect_x1, rect_y1, rect_x2, rect_y2):
			"""Returns whether a point (x, y) intersects with a given rectangle (rect_x1, rect_y1, rect_x2, rect_y2)"""
			return x >= rect_x1 and x <= rect_x2 and y >= rect_y1 and y <= rect_y2

		def set_mode(x, y):
			select_rad = 10
			x1, y1, x2, y2 = self.canvas_transform.coords()
			if   point_intersects_square_xyw(x, y, x1, y1, select_rad): # top left
				self.transform_mode.set("topleft")
			elif point_intersects_square_xyw(x, y, x2, y1, select_rad): # top right
				self.transform_mode.set("topright")
			elif point_intersects_square_xyw(x, y, x1, y2, select_rad): # bottom left
				self.transform_mode.set("bottomleft")
			elif point_intersects_square_xyw(x, y, x2, y2, select_rad): # bottom right
				self.transform_mode.set("bottomright")
			elif point_intersects_rect_xyxy(x, y, x1, y1, x2, y2): # middle (move)
				self.transform_mode.set("move")
			elif point_intersects_rect_xyxy(x, y, x1, y1 - select_rad, x2, y2): # top
				self.transform_mode.set("top")
			elif point_intersects_rect_xyxy(x, y, x2, y1, x2 + select_rad, y2): # right
				self.transform_mode.set("right")
			elif point_intersects_rect_xyxy(x, y, x1, y2, x2, y2 + select_rad): # bottom
				self.transform_mode.set("bottom")
			elif point_intersects_rect_xyxy(x, y, x1 - select_rad, y1, x1, y2): # left
				self.transform_mode.set("left")
			else:
				self.transform_mode.set("none")

		def mouse_click(event):
			# get event coords
			x, y = coords(event)
			self.canvas.mouse_down = True
			if self.transform_state:
				# if user clicks away, remove the transform
				if self.transform_mode == "none":
					self.transform_state.set(False)
					self.canvas_transform.delete(self.canvas)
				set_mode(x, y)
				self.canvas_transform.set_offset(x, y)
				self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state:
				self.canvas_selection.create(self.canvas, x, y, outline="red", dash=(3, 5), fill=None)

		def mouse_move(event):
			# limit the amount of times the event is executed
			self.m_movement += 1
			if self.m_movement % 2: return
			# get event coords
			x, y = coords(event)
			# update the footer info
			self.i_coords.set(x=x, y=y)
			if self.transform_state:
				# if the mouse is held down, perform the scaling transformation
				if self.canvas.mouse_down:
					self.canvas_transform.adjust(self.canvas, self.transform_mode, x, y)
				# if it's not, just update the cursor
				if not self.canvas.mouse_down:
					set_mode(x, y)
					self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state and self.canvas.mouse_down:
				self.canvas_selection.adjust(self.canvas, x, y)

		def mouse_release(event):
			x, y = coords(event)
			self.canvas.mouse_down = False
			self.remove_focus()
			if self.transform_state:
				set_mode(x, y)
				self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state:
				# use the selection coordinates to create a transformer
				x1, y1, x2, y2 = self.canvas_selection.delete(self.canvas)
				self.marker_state.set(False)
				self.canvas_transform.create(self.canvas, x1, y1, x2, y2)
				self.transform_state.set(True)
		
		# set up the canvas and local variables
		self.canvas_selection = SelectionManager()
		self.canvas_transform = TransformManager()
		self.canvas = Canvas(parent, bg="white")
		self.canvas.pack(fill="both", expand=1)
		self.canvas.bind("<Motion>", mouse_move)
		self.canvas.bind("<Button-1>", mouse_click)
		self.canvas.bind("<ButtonRelease-1>", mouse_release)
		self.canvas.mouse_down = False

root = Tk()
app = UI(root)
root.mainloop()
