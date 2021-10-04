from math import exp
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tracker import Tracker
from PIL import ImageTk

class Console(ScrolledText):
	def __init__(self, *args, **kwargs) -> None:
		import sys
		super().__init__(*args, **kwargs)
		self.ch_count = 0

		class ConsoleManager:
			def __init__(self, widget: tk.Text, old_stdout: sys.stdout):
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

class InfoText(tk.Label):
	def __init__(self, *args, **kwargs) -> None:
		self.text = tk.StringVar()
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

class ObjectInfo():
	def __init__(self, root, prop_list: list) -> None:
		self.prop = prop_list
		self.root = root

		def validate_number(input_):
			if (input_.isdigit() and int(input_) < 1000) or input_ == "": return True
			return False
		self.validate_number = (self.root.register(validate_number), "%P")

	def set_functions(self, remove_focus, deselect_object, delete_object):
		self.deselect_object = deselect_object
		self.delete_object = delete_object
		self.remove_focus = remove_focus

	def clear(self):
		"""Deletes all widgets."""
		for i in self.prop: i.destroy()

	def add_separator(self, size: int):
		"""Adds an empty separator of size (size)"""
		self.prop.append(tk.Frame(self.root))
		self.prop[-1].pack(ipady=size)

	def add_deselect(self):
		"""Adds a <Deselect> button which, when clicked, deselects the selected object."""
		self.prop.append(tk.Button(self.root, text="Deselect", command=self.deselect_object))
		self.prop[-1].pack(pady=2)

	def add_delete(self):
		"""Adds a <Delete> button which, when clicked, deletes the selected object."""
		self.prop.append(tk.Button(self.root, text="Delete", fg="red", command=self.delete_object))
		self.prop[-1].pack(pady=2)

	def add_title(self, text: str):
		"""Adds a title text, must go first."""
		self.prop.append(tk.Label(self.root, text=text))
		self.prop[-1].pack()
		self.add_separator(5)

	def add_property(self, name: str, value: str):
		wrapper = tk.Frame(self.root)
		label1  = tk.Label(wrapper, text=name)
		label1.pack(side="left")
		label2  = tk.Label(wrapper, text=str(value))
		label2.pack(side="right")
		self.prop.append(wrapper)
		wrapper.pack(fill="x")
	
	def add_numeric_property(self, name: str, default: int=0, onchange=None, from_=0, to=999):
		"""Adds a numeric property to the object."""
		var = None
		if not onchange is None:
			var = tk.StringVar()
			var.set(str(default))
			var.trace("w", lambda x,y,z,v=var: onchange(v))
		wrapper = tk.Frame(self.root)
		wrapper.pack(fill="x")
		label = tk.Label(wrapper, text=name)
		label.pack(side="left")
		spinbox = ttk.Spinbox(wrapper, from_=from_, to=to, width=0, validate="key", validatecommand=self.validate_number)
		if not onchange is None: spinbox.config(textvariable=var)
		spinbox.pack(side="right", fill="x", expand=1)
		spinbox.bind("<Return>", self.remove_focus)
		spinbox.bind("<Escape>", self.remove_focus)
		self.prop.append(wrapper)

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

	def create(self, canvas: tk.Canvas, x: int, y: int, **kwargs) -> None:
		self.shape_id = canvas.create_rectangle(x, y, x, y, **kwargs)
		self.x1, self.y1, self.x2, self.y2 = (x, y, x, y)
	
	def adjust(self, canvas: tk.Canvas, x: int, y: int) -> None:
		if not self.shape_id: return
		self.x2, self.y2 = (x, y)
		rx1 = self.x1 if self.x1 < self.x2 else self.x2
		ry1 = self.y1 if self.y1 < self.y2 else self.y2
		rx2 = self.x1 if self.x1 > self.x2 else self.x2
		ry2 = self.y1 if self.y1 > self.y2 else self.y2
		canvas.coords(self.shape_id, rx1, ry1, rx2, ry2)
	
	def delete(self, canvas: tk.Canvas) -> tuple:
		canvas.delete(self.shape_id)
		x1 = self.x1 if self.x1 < self.x2 else self.x2
		y1 = self.y1 if self.y1 < self.y2 else self.y2
		x2 = self.x1 if self.x1 > self.x2 else self.x2
		y2 = self.y1 if self.y1 > self.y2 else self.y2
		coords = (x1, y1, x2, y2)
		self.__init__()
		return coords

class BoolSwitch:
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

class ObjectSwitch:
	def __init__(self) -> None:
		self.object = None
		self.onchange = None

	def __len__(self) -> bool:
		return not not self.object

	def __repr__(self) -> str:
		return repr(self.object)

	def __eq__(self, other) -> bool:
		return self.object == other

	def set(self, selected_object: object):
		if self.object != selected_object:
			if self.onchange: self.onchange(selected_object)
		self.object = selected_object

class TransformSwitch:
	def __init__(self) -> None:
		self.state = "none"
		self.states = ["move", "topleft", "top", "topright", "right", "bottomright", "bottom", "bottomleft", "left", "none"]
		self.fixed = False
		self.onchange = None

	def __repr__(self) -> str:
		return str(self.state)

	def __eq__(self, other) -> bool:
		return self.state == str(other).lower()
	
	def set(self, state: str, fixed: bool) -> None:
		state = str(state).lower()
		if not state in self.states: return 
		if self.state != state or self.fixed != fixed:
			if self.onchange: self.onchange(state)
		self.state = state
		self.fixed = fixed
	
	def to_cursor(self):
		return ["fleur", "size_nw_se", "size_ns", "size_ne_sw", "size_we", "size_nw_se", "size_ns", "size_ne_sw", "size_we", ""][self.states.index(self.state)]

class TransformManager:
	def __init__(self) -> None:
		self.show_handles  = True
		self.fixed_radtio  = False
		self.center_marker = None
		self.main_rect     = None
		self.handles       = None
		self.ratio         = 1
		self.x1            = 0
		self.y1            = 0
		self.x2            = 0
		self.y2            = 0
		self.ox            = 0
		self.oy            = 0
	
	def create(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int) -> None:
		"""Creates the necessary objects on the canvas."""
		self.x1, self.y1, self.x2, self.y2 = (x1, y1, x2, y2)
		self.main_rect = canvas.create_rectangle(0, 0, 0, 0, outline="#558ef0", fill=None)
		self.center_marker = [canvas.create_line(0, 0, 0, 0, fill="#558ef0") for i in range(2)]
		self.handles = [canvas.create_rectangle(0, 0, 0, 0, outline="#558ef0", fill="#ffffff") if i != 4 else None for i in range(9)]
		self.update(canvas)

	def update(self, canvas: tk.Canvas) -> None:
		"""Update the objects on the canvas."""
		if not self.center_marker or not self.main_rect or not self.handles:
			raise Exception("Please call 'create' function first")
		# make sure (rx1, ry1) is on the top left and (rx2, ry2) on the bottom right
		rx1 = self.x1 if self.x1 < self.x2 else self.x2
		ry1 = self.y1 if self.y1 < self.y2 else self.y2
		rx2 = self.x1 if self.x1 > self.x2 else self.x2
		ry2 = self.y1 if self.y1 > self.y2 else self.y2
		canvas.coords(self.main_rect, rx1, ry1, rx2, ry2)

		# update the center marker to be in the middle
		cx = round(rx1+(rx2-rx1)/2)
		cy = round(ry1+(ry2-ry1)/2)
		canvas.coords(self.center_marker[0], cx-3, cy,   cx+4, cy)
		canvas.coords(self.center_marker[1], cx,   cy-3, cx,   cy+4)

		w = 7 # handle size
		for i in range(9):
			if i == 4: continue
			# if show_handles is false, hide the handles
			if self.show_handles: canvas.itemconfig(self.handles[i], state="normal")
			else: canvas.itemconfig(self.handles[i], state="hidden"); continue
			# if fixed_ratio is true, hide the in-between handles
			if self.fixed_radtio and not (i+1) % 2: canvas.itemconfig(self.handles[i], state="hidden"); continue
			else: canvas.itemconfig(self.handles[i], state="normal")
			# set the handle coordinates
			x, y = (int(i % 3), int(i / 3))
			hx = rx1 + x * (rx2-rx1)/2
			hy = ry1 + y * (ry2-ry1)/2
			canvas.coords(self.handles[i], hx - w/2, hy - w/2, hx + w/2, hy + w/2)
	
	def delete(self, canvas: tk.Canvas) -> None:
		"""Delete the canvas objects and reset the class variables."""
		if self.main_rect: canvas.delete(self.main_rect)
		for i in range(9):
			if i < 2  and self.center_marker: canvas.delete(self.center_marker[i])
			if i != 4 and self.handles: canvas.delete(self.handles[i])
		self.__init__()
	
	def adjust(self, canvas: tk.Canvas, mode: TransformSwitch, x: int, y: int) -> None:
		if "top" == mode.state:
			self.y1, self_x1 = y, self.x1
			self.x1 = ((self_x1 + self.x2) - (self.y2 - self.y1) * self.ratio) / 2 if mode.fixed else self.x1
			self.x2 = ((self_x1 + self.x2) + (self.y2 - self.y1) * self.ratio) / 2 if mode.fixed else self.x2
		if "right" == mode.state:
			self.x2, self_y1 = (x, self.y1)
			self.y1 = ((self_y1 + self.y2) - (self.x2 - self.x1) / self.ratio) / 2 if mode.fixed else self.y1
			self.y2 = ((self_y1 + self.y2) + (self.x2 - self.x1) / self.ratio) / 2 if mode.fixed else self.y2
		if "bottom" == mode.state:
			self.y2, self_x1 = (y, self.x1)
			self.x1 = ((self_x1 + self.x2) - (self.y2 - self.y1) * self.ratio) / 2 if mode.fixed else self.x1
			self.x2 = ((self_x1 + self.x2) + (self.y2 - self.y1) * self.ratio) / 2 if mode.fixed else self.x2
		if "left" == mode.state:
			self.x1, self_y1 = (x, self.y1)
			self.y1 = ((self_y1 + self.y2) - (self.x2 - self.x1) / self.ratio) / 2 if mode.fixed else self.y1
			self.y2 = ((self_y1 + self.y2) + (self.x2 - self.x1) / self.ratio) / 2 if mode.fixed else self.y2
		if "topleft" == mode.state:
			self.x1 = ((self.x2 + x) - (self.y2 - y) * self.ratio) / 2 if mode.fixed else x
			self.y1 = ((self.y2 + y) - (self.x2 - x) / self.ratio) / 2 if mode.fixed else y
		if "topright" == mode.state:
			self.x2 = ((self.x1 + x) + (self.y2 - y) * self.ratio) / 2 if mode.fixed else x
			self.y1 = ((self.y2 + y) - (x - self.x1) / self.ratio) / 2 if mode.fixed else y
		if "bottomright" == mode.state:
			self.x2 = ((self.x1 + x) + (y - self.y1) * self.ratio) / 2 if mode.fixed else x
			self.y2 = ((self.y1 + y) + (x - self.x1) / self.ratio) / 2 if mode.fixed else y
		if "bottomleft" == mode.state:
			self.x1 = ((self.x2 + x) - (y - self.y1) * self.ratio) / 2 if mode.fixed else x
			self.y2 = ((self.y1 + y) + (self.x2 - x) / self.ratio) / 2 if mode.fixed else y
		if "move" == mode.state:
			cs = 15 # center size
			w = self.x2 - self.x1
			h = self.y2 - self.y1
			tc = (x - self.ox + w / 2, y - self.oy + h / 2) # transform center
			cc = (canvas.winfo_width()/2, canvas.winfo_height()/2) # canvas center
			if mode.fixed and tc[0] >= cc[0] - cs and tc[0] <= cc[0] + cs:
				x = cc[0] + self.ox - w/2
			if mode.fixed and tc[1] >= cc[1] - cs and tc[1] <= cc[1] + cs:
				y = cc[1] + self.oy - h/2
			self.x1 = x - self.ox
			self.y1 = y - self.oy
			self.x2 = self.x1 + w
			self.y2 = self.y1 + h
		self.update(canvas)

	def init_drag(self, x, y):
		"""Set up the manager to adjust properly. (call *once* before adjusting)"""
		self.reset_coords()
		self.set_offset(x, y)
		self.set_ratio()

	def set_offset(self, x, y) -> None:
		self.ox = x - self.x1
		self.oy = y - self.y1

	def set_ratio(self):
		self.ratio = (self.x2 - self.x1) / ((self.y2 - self.y1) or 1)

	def reset_coords(self):
		self.x1, self.y1, self.x2, self.y2 = self.coords()

	def coords(self) -> tuple:
		"""Get the coordinates tuple (x1, y1, x2, y2)"""
		x1, y1, x2, y2 = (self.x1, self.y1, self.x2, self.y2)
		if x1 > x2: x2 = x2 + x1; x1 = x2 - x1; x2 = x2 - x1
		if y1 > y2: y2 = y2 + y1; y1 = y2 - y1; y2 = y2 - y1
		return (x1, y1, x2, y2)

class ChooseImage:
	def __init__(self) -> None:
		self.image = 0
	
	def __new__(self) -> ImageTk.PhotoImage:
		from PIL import Image, ImageTk
		from tkinter import filedialog
		filepath = filedialog.askopenfilename(initialdir=folder+"src", title="Load an image", filetypes=(("Image files", ("*.png", "*.gif*", "*.jpg", "*.jpeg")), ("All files", ("*.*"))))
		if not filepath: return
		self.image = image = ImageTk.PhotoImage(Image.open(filepath))
		return image

folder = __file__[:__file__.rfind("/")+1]
objects = []

class UI(tk.Frame):
	def __init__(self, root: tk.Tk, *args, **kwargs):
		tk.Frame.__init__(self, root, *args, **kwargs)
		self.pack(fill="both", expand=1, padx=2, pady=2)
		self.root = root

		# set up the window
		self.root.title("Image GUI")
		self.root.geometry("800x480")
		self.root.resizable(0, 0)

		# set up globals
		self.transform_object = ObjectSwitch()
		self.transform_state = BoolSwitch()
		self.transform_mode = TransformSwitch()
		self.marker_state = BoolSwitch()
		self.m_movement = 0
		self.create_ui()

	def create_ui(self):
		self.footer = tk.Frame(self, relief="flat")
		self.footer.pack(side="bottom", fill="x")
		
		self.sidebar = tk.Frame(self, relief="groove", borderwidth=2)
		self.sidebar.pack(side="left", fill="y", ipadx=10)

		self.mainframe = tk.Frame(self, relief="flat")
		self.mainframe.pack(side="right", fill="both", expand=1)

		self.displayframe = tk.Frame(self.mainframe, relief="groove", borderwidth=2)
		self.displayframe.pack(side="top", fill="both", expand=1, anchor="n")
		
		# necessary. why? because fuck tkinter
		ttk.Label(self.sidebar, font=("Arial", 5), text=" "*40).pack()

		# self.console = Console(self.mainframe, bg="#0f0f0f", fg="white", height=6)
		# self.console.pack(side="top", fill="x")
		# self.console.config(blockcursor=1, selectbackground="#9a9a9a", insertbackground="#9a9a9a", takefocus=0)
		# self.console.bind("<Key>", lambda x: "break")
		# self.console.bind("<FocusIn>", lambda x: "break")

		self.setup_canvas(self.displayframe)
		self.i_coords = InfoText(self.footer)
		self.i_coords.pack(anchor="nw")
		self.i_coords.set(x=0, y=0)

		self.marker_state.onchange = self.change_marker_button_state
		self.draw_marker_button = tk.Button(self.sidebar, text="Draw marker", command=self.marker_state.toggle)
		self.draw_marker_button.pack(side="top", pady=5)

		self.load_image_button = tk.Button(self.sidebar, text="Load image", command=self.load_image_to_canvas)
		self.load_image_button.pack(side="top", pady=5)

		separator = ttk.Separator(self.sidebar, orient="horizontal")
		separator.pack(fill="x", padx=5, pady=5)

		self.transform_object.onchange = self.display_object_properties
		self.root.bind("<Delete>", self.delete_object)
		self.info_objects = [] # info objects. used for displaying information about selected object

	def remove_focus(self, *args, **kwargs):
		"""Remove focus from a text area."""
		self.root.focus_set()

	def load_image_to_canvas(self):
		"""Load and display an image to canvas."""
		# ChooseImage() needs to be a class
		img = ChooseImage()
		if not img: return
		img_id = self.canvas.create_image(self.canvas.winfo_width()/2 - img.width() / 2, self.canvas.winfo_height()/2 - img.height() / 2, image=img, anchor="nw")
		x, y = self.canvas.coords(img_id)
		objects.append((img_id, x, y, x+img.width(), y+img.height()))
		self.canvas.tag_lower(img_id)

	def change_marker_button_state(self, state):
		"""Change style of the <Draw marker> button."""
		if state: self.draw_marker_button.config(fg="red", relief="sunken")
		else: self.draw_marker_button.config(fg="black", relief="raised")

	def reset_transform(self):
		self.canvas_transform.delete(self.canvas)
		self.transform_mode.set("none", False)
		self.transform_state.set(False)
		self.transform_object.set(None)
		self.canvas.config(cursor="")

	def delete_object(self, *args, **kwargs):
		"""Deletes the selected object."""
		obj = self.transform_object.object
		if obj in objects: objects.remove(obj)
		if isinstance(obj, Tracker):
			obj.tk_undraw(self.canvas)
		elif isinstance(obj, tuple):
			self.canvas.delete(obj[0])
		elif isinstance(obj, int):
			self.canvas.delete(obj)
		self.reset_transform()

	def deselect_object(self, *args, **kwargs):
		if self.transform_object == None: return
		if isinstance(self.transform_object.object, Tracker):
			self.transform_object.object.tk_draw(self.canvas)
			objects.insert(0, self.transform_object.object)
		elif isinstance(self.transform_object.object, tuple):
			obj = self.transform_object.object
			objects.append((obj[0],) + self.canvas_transform.coords())
		self.reset_transform()
	
	def display_object_properties(self, object_):
		"""Display the info and adjustable properties onto the sidebar."""
		prop = ObjectInfo(self.sidebar, self.info_objects)
		prop.set_functions(self.remove_focus, self.deselect_object, self.delete_object)
		prop.clear()

		if isinstance(object_, Tracker):
			def set_tracker_bg(var):
				self.transform_object.object.set(bg_margin=int(var.get() or "0"))
				self.transform_object.object.tk_draw(self.canvas)
			
			prop.add_title("Tracker")
			prop.add_numeric_property("BG size: ", default=object_.bg_margin, onchange=set_tracker_bg)	
			prop.add_separator(5)
			prop.add_deselect()
			prop.add_delete()
		elif isinstance(object_, tuple):
			prop.add_title("Image")
			prop.add_property("Width:",  object_[3]-object_[1])
			prop.add_property("Height:", object_[4]-object_[2])
			prop.add_separator(5)
			prop.add_deselect()
			prop.add_delete()
		elif not object_ is None:
			prop.add_separator(5)
			prop.add_deselect()
			prop.add_delete()

	def setup_canvas(self, parent: tk.Widget):
		def coords(event):
			"""Get X and Y coordinates from a mouse event."""
			return (int(event.x), int(event.y))
		
		def point_intersects_square_center_xyw(x, y, square_x, square_y, square_rad):
			"""Returns whether a point (x, y) intersects with a given square centered at (x=square_x, y=square_y, w=square_rad, h=square rad)"""
			return x >= square_x - square_rad and x <= square_x + square_rad and y >= square_y - square_rad and y <= square_y + square_rad
		
		def point_intersects_rect_xywh(x, y, rect_x, rect_y, rect_width, rect_height):
			"""Returns whether a point (x, y) intersects with a given rectangle (x=rect_x, y=rect_y, w=rect_width, h=rect_height)"""
			return x >= rect_x and x <= rect_x + rect_width and y >= rect_y and y <= rect_y + rect_height

		def point_intersects_rect_xyxy(x, y, rect_x1, rect_y1, rect_x2, rect_y2):
			"""Returns whether a point (x, y) intersects with a given rectangle (rect_x1, rect_y1, rect_x2, rect_y2)"""
			return x >= rect_x1 and x <= rect_x2 and y >= rect_y1 and y <= rect_y2

		def set_transform_mode(x, y):
			"""Set transforming mode based on which handle the user grabbed."""
			select_rad = 10
			handles = self.canvas_transform.show_handles
			fixed_r = self.canvas_transform.fixed_radtio
			x1, y1, x2, y2 = self.canvas_transform.coords()
			if   point_intersects_square_center_xyw(x, y, x1, y1, select_rad) and handles: # top left
				self.transform_mode.set("topleft", fixed_r)
			elif point_intersects_square_center_xyw(x, y, x2, y1, select_rad) and handles: # top right
				self.transform_mode.set("topright", fixed_r)
			elif point_intersects_square_center_xyw(x, y, x1, y2, select_rad) and handles: # bottom left
				self.transform_mode.set("bottomleft", fixed_r)
			elif point_intersects_square_center_xyw(x, y, x2, y2, select_rad) and handles: # bottom right
				self.transform_mode.set("bottomright", fixed_r)
			elif point_intersects_rect_xyxy(x, y, x1, y1 - select_rad, x2, y1 + select_rad) and handles: # top
				self.transform_mode.set("top", fixed_r)
			elif point_intersects_rect_xyxy(x, y, x2 - select_rad, y1, x2 + select_rad, y2) and handles: # right
				self.transform_mode.set("right", fixed_r)
			elif point_intersects_rect_xyxy(x, y, x1, y2 - select_rad, x2, y2 + select_rad) and handles: # bottom
				self.transform_mode.set("bottom", fixed_r)
			elif point_intersects_rect_xyxy(x, y, x1 - select_rad, y1, x1 + select_rad, y2) and handles: # left
				self.transform_mode.set("left", fixed_r)
			elif point_intersects_rect_xyxy(x, y, x1, y1, x2, y2): # middle (move)
				self.transform_mode.set("move", fixed_r)
			else:
				self.transform_mode.set("none", False)

		def select_object(x, y):
			global objects
			for i, o in enumerate(objects):
				x1, y1, x2, y2 = (None,) * 4
				self.canvas_transform.show_handles = True
				if isinstance(o, Tracker):
					x1, y1, x2, y2 = (o.x, o.y, o.x+o.width, o.y+o.height)
				elif isinstance(o, tuple):
					x1, y1, x2, y2 = o[1:]
					self.canvas_transform.show_handles = False
				elif isinstance(o, int):
					x1, y1, x2, y2 = self.canvas.coords(o)
				if point_intersects_rect_xyxy(x, y, x1, y1, x2, y2):
					objects.pop(i) # remove it from <objects> list
					self.transform_object.set(o)
					self.canvas_transform.create(self.canvas, x1, y1, x2, y2)
					self.transform_state.set(True)
					return
			self.transform_object.set(None)

		def deselect_object():
			if self.transform_object == None: return
			if isinstance(self.transform_object.object, Tracker):
				self.transform_object.object.tk_draw(self.canvas)
				objects.insert(0, self.transform_object.object)
			elif isinstance(self.transform_object.object, tuple):
				obj = self.transform_object.object
				objects.append((obj[0],) + self.canvas_transform.coords())
			self.transform_object.set(None)

		def apply_transformations():
			x1, y1, x2, y2 = self.canvas_transform.coords()
			if isinstance(self.transform_object.object, Tracker):
				self.transform_object.object.set(x=x1, y=y1, width=x2-x1, height=y2-y1)
				self.transform_object.object.tk_draw(self.canvas)
			elif isinstance(self.transform_object.object, tuple):
				self.canvas.coords(self.transform_object.object[0], x1, y1)
			elif isinstance(self.transform_object.object, int):
				self.canvas.coords(self.transform_object.object, x1, y1, x2, y2)

		def key_press(event):
			key = event.keycode
			if key == 16:
				self.canvas.shift_down = True
			if self.canvas.mouse_down:
				c = self.canvas.mouse_coords
				self.transform_mode.fixed = self.canvas.shift_down
				self.canvas_transform.adjust(self.canvas, self.transform_mode, c[0], c[1])
				apply_transformations()
		
		def key_release(event):
			key = event.keycode
			if key == 16:
				self.canvas.shift_down = False
			if self.canvas.mouse_down:
				c = self.canvas.mouse_coords
				self.transform_mode.fixed = self.canvas.shift_down
				self.canvas_transform.adjust(self.canvas, self.transform_mode, c[0], c[1])
				apply_transformations()

		def mouse_click(event):
			global objects
			# get mouse coords
			x, y = coords(event)
			self.canvas.mouse_down = True
			self.canvas.mouse_coords = coords(event)
			if self.transform_state:
				# if user clicks away from the transform, remove the transformation manager
				if self.transform_mode == "none":
					deselect_object()
					self.canvas_transform.delete(self.canvas)
					self.transform_state.set(False)
				set_transform_mode(x, y)
				self.canvas_transform.init_drag(x, y) # set up the transformation manager
				self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state:
				# create a marker to vizualize where the Tracker is being placed
				self.canvas_marker.create(self.canvas, x, y, outline="red", dash=(3, 5), fill=None)
			if not self.transform_state and not self.marker_state:
				select_object(x, y)

		def mouse_move(event):
			self.m_movement += 1 # limit the times the event can be triggered
			if self.m_movement % 2: return
			# get event coords
			x, y = coords(event)
			# update the footer info
			self.i_coords.set(x=x, y=y)
			self.canvas.mouse_coords = coords(event)
			if self.transform_state:
				# if the mouse is held down, perform the transformation
				if self.canvas.mouse_down:
					self.transform_mode.fixed = self.canvas.shift_down
					self.canvas_transform.adjust(self.canvas, self.transform_mode, x, y)
					apply_transformations()
				# if it's not, just update the cursor
				if not self.canvas.mouse_down:
					set_transform_mode(x, y)
					self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state and self.canvas.mouse_down:
				self.canvas_marker.adjust(self.canvas, x, y)

		def mouse_release(event):
			x, y = coords(event)
			self.remove_focus()
			self.canvas.mouse_down = False
			self.canvas.mouse_coords = coords(event)
			if self.transform_state:
				set_transform_mode(x, y)
				self.canvas_transform.reset_coords()
				self.canvas.config(cursor=self.transform_mode.to_cursor())
			if self.marker_state:
				self.deselect_object()
				# create a Tracker at marker coordinates and select it
				x1, y1, x2, y2 = self.canvas_marker.delete(self.canvas)
				self.marker_state.set(False)
				self.transform_object.set(Tracker(x1, y1, x2-x1, y2-y1, mode="TOPLEFT"))
				self.transform_object.object.tk_draw(self.canvas)
				self.canvas_transform.create(self.canvas, x1, y1, x2, y2)
				self.transform_state.set(True)
		
		# set up the canvas and local variables
		self.canvas_marker = SelectionManager()
		self.canvas_transform = TransformManager()
		self.canvas = tk.Canvas(parent, bg="white")
		self.canvas.pack(fill="both", expand=1)
		self.canvas.bind("<Motion>", mouse_move)
		self.canvas.bind("<Button-1>", mouse_click)
		self.canvas.bind("<ButtonRelease-1>", mouse_release)
		self.root.bind("<KeyPress>", key_press)
		self.root.bind("<KeyRelease>", key_release)
		self.root.bind("<Escape>", self.deselect_object)
		self.canvas.mouse_down = False
		self.canvas.shift_down = False
		self.canvas.mouse_coords = (0, 0)

root = tk.Tk()
app = UI(root)
root.mainloop()
