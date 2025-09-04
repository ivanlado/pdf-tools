from PyPDF2 import PdfReader, PdfWriter
from .models import CropSetting, Crop
import os

class PDFProcessor:
    def __init__(self, filepath=None):
        self.num_pages = None
        self.filepath = filepath
        self.output_filepath = None
        self.reader = None
        self.writer = PdfWriter()
        self.delete_pages = []
        
    def load_pdf(self):
        """Load a PDF file."""
        try:
            self.reader = PdfReader(self.filepath)
            self.num_pages = len(self.reader.pages)
        except FileNotFoundError:
            raise ValueError("File not found")
        except Exception as e:
            raise ValueError("Error reading PDF file")
        
    def crop_pdf(self, crop_setting: CropSetting):
        """Crop all pages of the PDF to the same coordinates."""
        original_size_x, original_size_y = float(self.reader.pages[0].mediabox.right), float(self.reader.pages[0].mediabox.top)
        # for i in range(self.num_pages):
        for i in range(self.num_pages):
            page = self.reader.pages[i]
            crop = crop_setting.get_crop_factors_trans(i + 1)
            page.cropbox.lower_left = (int(crop.get_coords()[0] * original_size_x), int(crop.get_coords()[1] * original_size_y))
            page.cropbox.upper_right = (int(crop.get_coords()[2] * original_size_x), int(crop.get_coords()[3] * original_size_y))
        
            
    def set_delete_pages(self, deleted_pages: list[int]):
        """Set pages to be deleted (1-indexed)."""
        self.delete_pages = deleted_pages
            
    def set_filepath(self, filepath: str):
        self.filepath = filepath  
        self.output_filepath = self._generate_output_filename() 
        
    def _generate_output_filename(self):
        if self.filepath:
            filename = os.path.basename(self.filepath)
            base, ext = os.path.splitext(filename)
            base += "_edited"
            output_filepath = os.path.join(os.path.dirname(self.filepath), f"{base}{ext}")
            print("geenrated output filename:", output_filepath)
            return output_filepath
        else:
            return ""
    
    def save_pdf(self):
        self.writer = PdfWriter()
        for i, page in enumerate(self.reader.pages):
            if not self.delete_pages[i]:
                self.writer.add_page(page)
        print("Saving to:", self.output_filepath)
        with open(self.output_filepath, "wb") as f:
            self.writer.write(f)
        
    