from core.pdf_processor import PDFProcessor
from gui.main_window import MainWindow
import tkinter as tk


def main():
    # PDF Processor instance
    pdf_processor = PDFProcessor()
    # Create and run GUI
    root = tk.Tk()
    root.withdraw()
    app = MainWindow(root, pdf_processor)
    app.setup_ui()
    root.mainloop() 


if __name__ == "__main__":
    main()