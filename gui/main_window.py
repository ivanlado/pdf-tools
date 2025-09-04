from cProfile import label
from logging import root
from gui.pdf_viewer import PdfViewer
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
from core.models import CropSetting, Crop
import os


            

class MainWindow:
    def __init__(self, root, pdf_processor):
        super().__init__()
        self.root = root
        self.pdf_processor = pdf_processor
        self.pdf_viewer = PdfViewer()
        
        self.filepath = self.choose_pdf()
        if self.filepath:
            self.pdf_processor.set_filepath(self.filepath)
            # Loading the PDF processor
            self.pdf_processor.load_pdf()
            # Loading the PDF viewer, so that the images can be displayed on the GUI
            self.pdf_viewer.load_pdf(self.filepath)
            # show the root window
            self.root.deiconify()
            
            self.num_pages = self.pdf_processor.num_pages
            self.current_page = 1
            self.image_size = self.pdf_viewer.size_img
            self.current_crop_coords = [0, 0, self.pdf_viewer.size_img[0], self.pdf_viewer.size_img[1]]
            crops = [Crop(0, 0, self.pdf_viewer.size_img[0], self.pdf_viewer.size_img[1]) for _ in range(self.num_pages)]
            self.crop_settings = CropSetting(self.num_pages, crops, self.pdf_viewer.size_img[0], self.pdf_viewer.size_img[1])
            self.is_deleted = [False for _ in range(self.num_pages)]
            
        else: 
            messagebox.showinfo("No PDF file selected.", "No PDF file selected. Exiting application.")
            self.root.destroy()
        
        self.delete_btn_text = "Delete page"
        
    def setup_ui(self):
        """Set up the user interface."""
        # Default font family: Segoe UI
        # Default font size: 9
        # Default font weight: normal
        # Top frame for title and page number
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=7)
        self.root.grid_columnconfigure(1, weight=3)
        # ================= LEFT COLUMN ================= 
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.top_frame = tk.Frame(left_frame, padx=10, pady=10)
        self.top_frame.pack(fill="x")
        title_label = tk.Label(self.top_frame, font=("Segoe UI", 12), text="Title of the pdf: " + self.filepath)
        title_label.pack()
        self.number_page_label = tk.Label(self.top_frame, font=("Segoe UI", 10), text=f"Page {self.current_page}/{self.num_pages}")
        self.number_page_label.pack()
        # Canvas for displaying images and cropping rectangle
        self.canvas = tk.Canvas(left_frame, width=self.pdf_viewer.size_img[0], height=self.pdf_viewer.size_img[1], bg='white', cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Add 2 listeners to canvas for mouse events to capture crop rectangle
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.load_page()
        # Frame for buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack()
        # Btns for pages navigation
        # Left button
        # Left button
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=5)

        # Left button
        tk.Button(btn_frame, text="Open new pdf", command=self.choose_pdf).pack(side="left")
        # Spacer (between left and center group)
        tk.Frame(btn_frame).pack(side="left", expand=True, fill="x")
        # Center group
        center_frame = tk.Frame(btn_frame)
        center_frame.pack(side="left")
        tk.Button(center_frame, text="Previous page", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(center_frame, text="Next page", command=self.next_page).pack(side="left", padx=5)

        # Spacer (between center group and right)
        tk.Frame(btn_frame).pack(side="left", expand=True, fill="x")

        # Right button
        tk.Button(btn_frame, text="Apply changes and finish", command=self.apply_changes).pack(side="left")

        self.__setup_right_col_ui()
        
    

    def __setup_right_col_ui(self):
        right_frame = tk.Frame(self.root, bg="lightgray")
        right_frame.grid(row=0, column=1, sticky="nsew")
        # Spacer at the top
        tk.Frame(right_frame, bg="lightgray").pack(expand=True, fill="y")
        # Crop selection
        options_frame = tk.Frame(right_frame)
        options_frame.pack(padx=10, fill="x")
        self.apply_option = tk.StringVar(value="all")
        tk.Label(options_frame, text="Apply crop to:").pack(anchor="w")
        tk.Radiobutton(options_frame, text="All", variable=self.apply_option, value="all").pack(anchor="w")
        tk.Radiobutton(options_frame, text="This and following pages", variable=self.apply_option, value="following").pack(anchor="w")
        tk.Radiobutton(options_frame, text="Current Page", variable=self.apply_option, value= "current").pack(anchor="w")
        self.delete_btn = tk.Button(right_frame, text=self.delete_btn_text, command=self.delete_page)
        self.delete_btn.pack(fill="x", padx=10, pady=10)
        # Spacer at the bottom
        tk.Frame(right_frame, bg="lightgray").pack(expand=True, fill="y")
        
    def enable_delete_effect(self):
        self.canvas.itemconfigure(self.overlay, state="normal")
        if hasattr(self, 'delete_btn'):
            self.delete_btn.config(text="Restore page")
        
    def disable_delete_effect(self):
        self.canvas.itemconfigure(self.overlay, state="hidden")
        if hasattr(self, 'delete_btn'):
            self.delete_btn.config(text="Delete page")


        


    def choose_pdf(self):
        filename = filedialog.askopenfilename(title="Select a PDF", filetypes=[("PDF files", "*.pdf")])
        return filename
        
    def load_page(self):
        img = self.pdf_viewer.get_image(self.current_page)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)
        self.root.title(f"Page {self.current_page}/{self.num_pages}")
        if hasattr(self, 'rect'):
            self.rect = self.canvas.create_rectangle(self.current_crop_coords[0], self.current_crop_coords[1], self.current_crop_coords[2], self.current_crop_coords[3], outline='red', width=2)
        # Add overlay for deleted effect
        self.overlay = self.canvas.create_rectangle(0, 0, self.pdf_viewer.size_img[0], self.pdf_viewer.size_img[1], fill="black", stipple="gray50")
        if self.is_deleted[self.current_page - 1]:
            self.enable_delete_effect()
            self.delete_btn_text = "Restore page"
        else:
            self.disable_delete_effect()
            self.delete_btn_text = "Delete page"
        # Update GUI
        self.number_page_label.config(text=f"Page {self.current_page}/{self.num_pages}")

        
    def on_button_press(self, event):
        """Capture the initial position of the mouse click."""
        # Record the starting point of the crop rectangle
        if self.current_crop_coords:
            self.current_crop_coords[0], self.current_crop_coords[1] = event.x, event.y
        # Delete previous rectangle if it exists
        if hasattr(self, 'rect'):
            self.canvas.delete(self.rect)
        
    def on_move_press(self, event):
        """Draw a rectangle as the mouse is dragged."""
        # Update the rectangle as the mouse moves
        self.current_crop_coords[2], self.current_crop_coords[3] = event.x, event.y
        # Delete previous rectangle if it exists
        if hasattr(self, 'rect'):
            self.canvas.delete(self.rect)
        # Draw a rectangle from start point to current mouse position
        self.rect = self.canvas.create_rectangle(self.current_crop_coords[0], self.current_crop_coords[1], self.current_crop_coords[2], self.current_crop_coords[3], outline='red', width=2)
        
    def update_crop_settings(self):
        new_setting = Crop(self.current_crop_coords[0], self.current_crop_coords[1], self.current_crop_coords[2], self.current_crop_coords[3])
        if self.apply_option.get() == "all":
            pages = list(range(1, self.num_pages + 1))
        elif self.apply_option.get() == "following":
            pages = list(range(self.current_page, self.num_pages + 1))
        elif self.apply_option.get() == "current":
            pages = [self.current_page]
        self.crop_settings.update(new_setting, pages)
    
    def next_page(self):
        """Go to the next page."""
        if self.current_page < self.num_pages - 1:
            self.update_crop_settings()
            self.current_page += 1
            self.current_crop_coords = self.crop_settings.get_crop(self.current_page).get_coords()
            self.load_page()
            
    def prev_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.update_crop_settings()
            self.current_page -= 1
            self.current_crop_coords = self.crop_settings.get_crop(self.current_page).get_coords()
            self.load_page()
            
    def delete_page(self):
        self.is_deleted[self.current_page - 1] = not self.is_deleted[self.current_page - 1]
        if self.is_deleted[self.current_page - 1]:
            self.enable_delete_effect()
        else:
            self.disable_delete_effect()

    def apply_changes(self):
        # First, update the crop settings with the current crop
        self.update_crop_settings()
        # Call pdf_processor to apply the changes and save the new pdf
        self.pdf_processor.crop_pdf(self.crop_settings)
        self.pdf_processor.set_delete_pages(self.is_deleted)
        self.pdf_processor.save_pdf()
        # finish, close and show correct dialog with green tick and close
        self.root.destroy()
        # Show success message
        messagebox.showinfo("Success", "Operation completed successfully!")
        