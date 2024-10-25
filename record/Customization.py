import tkinter as tk

# Primary Color: Deep Sky Blue
# Hex: #00BFFF
# Secondary Color: Light Coral
# Hex: #F08080
# Background Color: Ghost White
# Hex: #F8F8FF
# Text Color: Dark Slate Gray
# Hex: #2F4F4F
# Accent Color: Gold
# Hex: #FFD700

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None, bg=None, fg="#2F4F4F"):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg= "#F8F8FF")
        self.command = command
        self.default_color = color
        # self.default_color = "#FFD700"  # Accent Color: Gold
        # self.default_color =  "#F8F8FF"
        self.active_color = "#00BFFF"  # Primary Color: Deep Sky Blue
        self.root_bg = "#F8F8FF"  # Background Color: Ghost White
        self.bg = "#FFD700"  # Set background color to Gold
        self.text = text
        if cornerradius > 0.5*width:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > 0.5*height:
            print("Error: cornerradius is greater than height.")
            return None

        rad = 2*cornerradius
        def shape():
            # top layer
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill= self.bg, tags="shape")
            # bottom layer
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=self.bg, outline=self.bg, tags="arc")
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=self.bg, outline=self.bg, tags="arc")
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=self.bg, outline=self.bg, tags="arc")
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=self.bg, outline=self.bg, tags="arc")

        id = shape()
        (x0,y0,x1,y1) = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.create_text(width/2, height/2, text=text, fill=fg, font=("Arial", 12, "bold"), tags="text")  # Text Color: Dark Slate Gray

        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        self.itemconfig("shape", fill=self.active_color, outline=self.active_color)
        self.itemconfig("arc", fill=self.active_color, outline=self.active_color)

    def _on_release(self, event):
        self.itemconfig("shape", fill=self.active_color, outline=self.active_color)
        self.itemconfig("arc", fill=self.active_color, outline=self.active_color)
        if self.command is not None:
            self.command()
    def change_foreground_color(self, new_color):
        self.itemconfig("text", fill=new_color)
        self.itemconfig("shape", fill=self.active_color, outline=self.active_color)
        self.itemconfig("arc", fill=self.active_color, outline=self.active_color)

    def disable_action(self):
        self.itemconfig("shape", fill=self.default_color, outline=self.default_color)
        self.itemconfig("arc", fill=self.default_color, outline=self.default_color)
        self.itemconfig("text", fill="#2F4F4F")  # Enabled text color: Dark Slate Gray
        self.unbind("<ButtonPress-1>")
        self.unbind("<ButtonRelease-1>")

    def enable_action(self):
        self.itemconfig("shape", fill=self.bg, outline=self.bg)
        self.itemconfig("arc", fill=self.bg, outline=self.bg)
        self.itemconfig("text", fill="#2F4F4F")  # Enabled text color: Dark Slate Gray
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def enable_action_no_color(self):
        # self.itemconfig("shape", fill=self.bg, outline=self.bg)
        # self.itemconfig("arc", fill=self.bg, outline=self.bg)
        self.itemconfig("text", fill="#2F4F4F")  # Enabled text color: Dark Slate Gray
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
# Usage
# root = tk.Tk()
# button = RoundedButton(root, 200, 50, 10, 2, "#00BFFF", "Click Me!", lambda: print("Clicked!"), bg="#F8F8FF", fg="#2F4F4F")  # Primary Color: Deep Sky Blue, Background Color: Ghost White, Text Color: Dark Slate Gray
# button.pack(pady=20)
# root.mainloop()