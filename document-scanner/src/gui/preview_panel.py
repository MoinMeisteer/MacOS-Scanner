from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow

from pdf2image import convert_from_path
import tempfile

import os


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Preview image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 500)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.image_label)

        # Button container
        button_layout = QHBoxLayout()

        # Accept button
        self.accept_button = QPushButton("Akzeptieren")
        self.accept_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.accept_button.clicked.connect(self.accept_document)

        # Reject button
        self.reject_button = QPushButton("Ablehnen")
        self.reject_button.setStyleSheet("background-color: #f44336; color: white;")
        self.reject_button.clicked.connect(self.reject_document)

        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.accept_button)
        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("Warte auf Dokument...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def show_preview(self, image_path):
        """Display the scanned document image"""
        try:
            print(f"Attempting to show preview for {image_path}")
            if not os.path.exists(image_path):
                self.status_label.setText(f"Datei nicht gefunden: {image_path}")
                return
            
            if image_path.lower().endswith('.pdf'):
                try:
                    with tempfile.TemporaryDirectory() as path:
                        images = convert_from_path(image_path, dpi=200)
                        if images:
                            first_page = images[0]
                            temp_path = os.path.join(path, 'preview.png')
                            first_page.save(temp_path, 'PNG')
                            pixmap = QPixmap(temp_path)
                        else:
                            self.status_label.setText("Keine Seiten im PDF gefunden")
                            return
                except Exception as pdf_error:
                    print(f"PDF conversion error: {pdf_error}")
                    self.status_label.setText("Fehler beim Konvertieren des PDFs")
                    return
            else:
                pixmap = QPixmap(image_path)

            if pixmap.QPimaxp.isNull():
                self.status_label.setText("Vorschau konnte nicht geladen werden")
                return
            
            scaled_pixmap = pixmap.scaled(400, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.status_label.setText("Bitte Dokument überprüfen")

        except Exception as e:
            print(f"Preview error: {str(e)}")
            self.status_label.setText(f"Fehler beim Laden der Vorschau: {str(e)}")
            self.image_label.clear()

    def accept_document(self):
        """Handle document acceptance"""
        if hasattr(self.main_window, 'process_accepted_document'):
            self.main_window.process_accepted_document()
        else:
            print("Warning: Main window has no process_accepted_document method")
        self.status_label.setText("Dokument akzeptiert")

    def reject_document(self):
        """Handle document rejection"""
        try:
            if isinstance(self.main_windows, QMainWindow):
                if hasattr(self.main_window, 'handle_rejected_document'):
                    self.main_window.handle_rejected_document()
                else:
                    print("Warning: Main window has no handle_rejected_document method")
            self.image_label.clear()
            self.status_label.setText("Dokument abgelehnt")
        except Exception as e:
            self.status_label.set_Text(f"Fehler beim Ablehnen des Dokuments: {str(e)}")

    def clear_preview(self):
        """Clear the preview panel"""
        self.image_label.clear()
        self.status_label.setText("Warte auf Dokument...")

    def show_preview(self, image_path):
        """Display the scanned document image"""
        try:
            if not os.path.exists(image_path):
                self.status_label.setText(f"Datei nicht gefunden: {image_path}")
                return
                
            if image_path.lower().endswith('.pdf'):
                # Convert PDF to image
                with tempfile.TemporaryDirectory() as path:
                    images = convert_from_path(image_path)
                    if images:
                        # Convert first page to QPixmap
                        first_page = images[0]
                        with tempfile.NamedTemporaryFile(suffix='.png') as tmp:
                            first_page.save(tmp.name, 'PNG')
                            pixmap = QPixmap(tmp.name)
                    else:
                        self.status_label.setText("Keine Seiten im PDF gefunden")
                        return
            else:
                # Handle normal image files
                pixmap = QPixmap(image_path)
                
            if pixmap.isNull():
                self.status_label.setText("Vorschau konnte nicht geladen werden")
                return
                
            scaled_pixmap = pixmap.scaled(400, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.status_label.setText("Bitte Dokument überprüfen")
            
        except Exception as e:
            self.status_label.setText(f"Fehler beim Laden der Vorschau: {str(e)}")
            self.image_label.clear()
