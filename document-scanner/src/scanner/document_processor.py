import os 
import shutil
from ocr.text_extractor import TextExtractor
from classifier.document_classifier import DocumentClassifier
import logging

class DocumentProcessor:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.classifier = DocumentClassifier()
        self.output_base = os.path.expanduser("~/Documents/Sortierte_Dokumente")  # Fixed variable name
        self._ensure_output_directories()

    def _ensure_output_directories(self):
        categories = ["Rechnungen", "Verträge", "Bescheinigungen", "Sonstiges"]
        for category in categories:
            path = os.path.join(self.output_base, category)  # Uses correct variable name
            os.makedirs(path, exist_ok=True)

    def process_document(self, document_path):
        try:
            # Extract text from document
            text = self.text_extractor.extract_text(document_path)
            
            # Get category and suggested filename
            category, suggested_filename = self.classifier.classify(text)
            
            # Ensure category is a string
            if not isinstance(category, str):
                logging.warning(f"Invalid category type: {type(category)}. Using 'Sonstiges'")
                category = "Sonstiges"

            # Create target directory path
            target_dir = os.path.join(self.output_base, category)
            
            # Get original filename and extension
            original_filename = os.path.basename(document_path)
            original_ext = os.path.splitext(document_path)[1]
            
            # Create new filename with extension
            if suggested_filename and isinstance(suggested_filename, str):
                new_filename = f"{suggested_filename}{original_ext}"
            else:
                new_filename = original_filename
            
            # Create target path
            target_path = os.path.join(target_dir, new_filename)
            
            # Handle duplicate filenames
            counter = 1
            while os.path.exists(target_path):
                base, ext = os.path.splitext(new_filename)
                target_path = os.path.join(target_dir, f"{base} ({counter}){ext}")
                counter += 1
            
            # Move the file
            shutil.move(document_path, target_path)
            logging.info(f"Dokument verarbeitet: {new_filename} -> {category}")
            
        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten des Dokuments: {str(e)}")
            raise