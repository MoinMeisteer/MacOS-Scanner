import pytesseract
from PIL import Image
import pdf2image
import logging

class TextExtractor:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

    def extract_text(self, file_path):
        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path)
            else:
                return self._extract_text_from_image(file_path)
        except Exception as e:
            logging.error(f"Fehler bei der Textextraktion: {str(e)}")
            raise

    
    def _extract_text_from_image(self, image_path):
        with Image.open(image_path) as img:
            text = pytesseract.image_to_string(img, lang='deu')
            return text.strip()
        
    
    def _extract_text_from_pdf(self, pdf_path):
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang='deu') + "\n"
        return text.strip()