from pdf2image import convert_from_path

PREFECH_SIZE = 5  # Size of the preview images

class PdfViewer:
    def __init__(self):
        self.images = []
        self.pdf_path = None
        self.size_img = None  # Size of the images, to be set after loading the PDF
        pass

    def load_pdf(self, pdf_path, max_height=800):
        self.pdf_path = pdf_path
        self.images = convert_from_path(self.pdf_path, dpi=100, first_page=1, last_page=PREFECH_SIZE)
        self.max_height = max_height
        # print images size
        for i, img in enumerate(self.images):
            print(f"Image {i+1} size: {img.size}")
        # Set the size of the images
        self.size_img = self.images[0].size if self.images else None
        # Resize size_img if its height exceeds max_height
        if self.size_img and self.size_img[1] > self.max_height:
            self.size_img = (int(self.size_img[0] * self.max_height / self.size_img[1]), self.max_height)
        
    def get_image(self, i):
        """Returns the image of page number i."""
        if i > len(self.images):
            self.images += convert_from_path(self.pdf_path, dpi=100, first_page=len(self.images)+1, last_page=len(self.images)+PREFECH_SIZE)
        img = self.images[i-1]
        if img.size[1] > self.max_height:
            img = img.resize((int(img.size[0] * self.max_height / img.size[1]), self.max_height))
        return img
