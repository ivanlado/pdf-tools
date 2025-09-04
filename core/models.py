"""
Data models for PDF cropping functionality.
"""


class Crop:
    """Represents a rectangular crop area with coordinates."""
    
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def get_coords(self):
        """Return crop coordinates as a list [x1, y1, x2, y2]."""
        return [self.x1, self.y1, self.x2, self.y2]


class CropSetting:
    """Manages crop settings for multiple pages of a PDF."""
    
    def __init__(self, number_pages: int, crops: list[Crop], xMax:int, yMax:int):
        self.number_pages = number_pages
        self.crop_setting = crops
        self.xMax = xMax
        self.yMax = yMax

    def update(self, new_setting: Crop, pages: list[int]):
        """Update crop settings for specified pages."""
        for page in pages:
            self.crop_setting[page - 1] = new_setting
            
    def get_crop(self, page: int):
        """Get crop setting for a specific page (1-indexed)."""
        return self.crop_setting[page - 1]
    
    def get_crop_factors_trans(self, page: int):
        """Get crop setting for a specific page (1-indexed) as factors of xMax and yMax."""
        crop = self.crop_setting[page - 1]
        new_crop = Crop(crop.x1 / self.xMax, 1-crop.y1 / self.yMax, crop.x2 / self.xMax, 1-crop.y2 / self.yMax)
        return new_crop
    
