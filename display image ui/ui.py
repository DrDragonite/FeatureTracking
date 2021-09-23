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
		self.origin_x = 0
		self.origin_y = 0

	def create(self, canvas: Canvas, x: int, y: int, **kwargs) -> None:
		self.shape_id = canvas.create_rectangle(x, y, x, y, **kwargs)
		self.origin_x = x
		self.origin_y = y
	
	def adjust(self, canvas: Canvas, x: int, y: int) -> None:
		if not self.shape_id: return
		rx1, ry1, rx2, ry2 = canvas.coords(self.shape_id)
		if x < self.origin_x: rx1 = x
		else: rx2 = x
		if y < self.origin_y: ry1 = y
		else: ry2 = y
		canvas.coords(self.shape_id, rx1, ry1, rx2, ry2)
	
	def delete(self, canvas: Canvas) -> None:
		canvas.delete(self.shape_id)
		origin = (self.origin_x, self.origin_y)
		self.shape_id = None
		self.origin_x = 0
		self.origin_y = 0
		return origin

class TransformManager:
	def __init__(self) -> None:
		self.allow_scaling = True
		self.fixed_radtio  = False
		self.main_rect     = None
		self.handles       = [None] * 8
		self.object        = None
		self.x1            = 0
		self.y1            = 0
		self.x2            = 0
		self.y2            = 0
	
	def create(self, canvas: Canvas, object: int):
		# create surrounding rectangle
		x1, y1, x2, y2 = canvas.coords(object)
		self.main_rect = canvas.create_rectangle(x1, y1, x2, y2, outline="#558ef0", fill=None)
		
		# create the little handles
		self.handles[0] = canvas.create_rectangle(x2)



class Switch:
	def __init__(self) -> None:
		self.state = False
		self.onchange = None

	def __len__(self) -> bool:
		return self.state

	def set(self, state: bool):
		if self.state != bool(state): 
			if self.onchange: self.onchange(bool(state))
		self.state = bool(state)
	
	def toggle(self):
		self.state = not self.state
		if self.onchange: self.onchange(self.state)

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

		self.marker_mode = Switch()
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
		self.console.insert("end", "> ")

		self.setup_canvas(self.displayframe)
		self.i_coords = InfoText(self.footer)
		self.i_coords.pack(anchor="nw")
		self.i_coords.set(x=0, y=0)

		self.marker_mode.onchange = self.change_marker_button_state
		self.draw_marker_button = Button(self.sideframe, text="Draw marker", command=self.marker_mode.toggle)
		self.draw_marker_button.pack(side="top", pady=5)

		self.load_image_button = Button(self.sideframe, text="Load image", command=self.load_image_to_canvas)
		self.load_image_button.pack(side="top", pady=5)

	def remove_focus(self):
		self.root.focus_set()

	def load_image_to_canvas(self):
		img = ChooseImage()
		if not img: return
		self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=img, anchor="center")

	def change_marker_button_state(self, state):
		if state:
			self.draw_marker_button.config(fg="red", relief="sunken")
		else:
			self.draw_marker_button.config(fg="black", relief="raised")

	def setup_canvas(self, parent: Widget):
		def coords(event):
			return (event.x, event.y)

		def mouse_click(event):
			x, y = coords(event)
			self.canvas.mouse_down = True
			if self.marker_mode:
				self.canvas_selection.create(self.canvas, x, y, outline="red", dash=(3, 5), fill=None)

		def mouse_move(event):
			x, y = coords(event)
			self.i_coords.set(x=x, y=y)
			if self.marker_mode and self.canvas.mouse_down:
				self.canvas_selection.adjust(self.canvas, x, y)

		def mouse_release(event):
			x, y = coords(event)
			self.canvas.mouse_down = False
			self.remove_focus()
			if self.marker_mode:
				x1 = x if x < self.canvas_selection.origin_x else self.canvas_selection.origin_x
				y1 = y if y < self.canvas_selection.origin_y else self.canvas_selection.origin_y
				x2 = x if x > self.canvas_selection.origin_x else self.canvas_selection.origin_x
				y2 = y if y > self.canvas_selection.origin_y else self.canvas_selection.origin_y
				self.canvas_selection.delete(self.canvas)
				self.marker_mode.set(False)

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
