from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QListWidget, QPushButton, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt
from .preview_panel import PreviewPanel
from PyQt5.QtCore import QTimer
from config.settings import WATCHED_FOLDER
import os
import subprocess

from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dokument Scanner")
        self.setMinimumSize(800, 600)
        self.log_list = QListWidget()
        self.sorting_timer = QTimer()
        self.sorting_timer.timeout.connect(self.process_pending_document)
        self.pending_document = None
        self.pending_category = None

        # Initialize all UI elements as class attributes first
        self.status_label = QLabel("Warte auf neue Dokumente...")
        self.scan_button = QPushButton("Dokument scannen")
        self.doc_list = QListWidget()
        self.category_label = QLabel("Kategorie:")
        self.category_combo = QComboBox()
        self.save_category_btn = QPushButton("Kategorie speichern")
        self.preview_panel = PreviewPanel(self)

        # Then set up the UI
        self.setup_ui()

    def setup_ui(self):
        # HauptWidget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Oberer Bereich: Scan Button und Status
        top_layout = QHBoxLayout()
        self.scan_button.clicked.connect(self.start_scan)
        top_layout.addWidget(self.scan_button)
        top_layout.addWidget(self.status_label)
        layout.addLayout(top_layout)

        # LOG list
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Sortierer-log:"))
        log_layout.addWidget(self.log_list)
        layout.addLayout(log_layout)

        # Mittlerer Bereich: Preview und Dokumentenliste
        middle_layout = QHBoxLayout()
        
        # Linke Seite: Dokumentenliste und Kategorie
        left_panel = QVBoxLayout()
        self.doc_list.currentItemChanged.connect(self.on_document_selected)
        left_panel.addWidget(QLabel("Dokumente:"))
        left_panel.addWidget(self.doc_list)
        
        # Kategorie Bereich
        category_layout = QHBoxLayout()
        self.category_combo.addItems(["Rechnung", "Vertrag", "Mahnung", "Sonstiges"])
        self.save_category_btn.clicked.connect(self.save_category)
        
        category_layout.addWidget(self.category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addWidget(self.save_category_btn)
        left_panel.addLayout(category_layout)
        
        middle_layout.addLayout(left_panel)
        middle_layout.addWidget(self.preview_panel)
        
        layout.addLayout(middle_layout)

    def on_document_selected(self, current, previous):
        """Wird aufgerufen, wenn ein Dokument in der Liste ausgewählt wird"""
        if current:
            doc_path = current.data(Qt.UserRole)
            print(f"Selected document path: {doc_path}")  # Debug-Ausgabe
            if doc_path and os.path.exists(doc_path):
                self.preview_panel.show_preview(doc_path)
                try:
                    category = self.get_document_category(doc_path)
                    index = self.category_combo.findText(category)
                    if index >= 0:
                        self.category_combo.setCurrentIndex(index)
                except Exception as e:
                    print(f"Error getting category: {e}") 

    def save_category(self):
        """Speichert die ausgewählte Kategorie für das aktuelle Dokument"""
        current_item = self.doc_list.currentItem()
        if current_item:
            doc_path = current_item.data(Qt.UserRole)
            new_category = self.category_combo.currentText()
            self.update_document_category(doc_path, new_category)
            self.status_label.setText(f"Kategorie auf {new_category} geändert")

    def update_document_category(self, doc_path, new_category):
        """Aktualisiert die Kategorie eines Dokuments"""
        self.pending_document = doc_path
        self.pending_category = new_category
        self.status_label.setText(f"Verschiebe Dokument in {new_category}...")
        self.sorting_timer.start(5000)
        try:
            # Erstelle Kategorie-Ordner im WATCHED_FOLDER falls nicht vorhanden
            category_path = os.path.join(WATCHED_FOLDER, new_category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            
            # Neuer Pfad für das Dokument
            new_path = os.path.join(category_path, os.path.basename(doc_path))
            
            # Wenn die Zieldatei bereits existiert, füge Zeitstempel hinzu
            if os.path.exists(new_path):
                base, ext = os.path.splitext(os.path.basename(doc_path))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = os.path.join(category_path, f"{base}_{timestamp}{ext}")
            
            # Verschiebe die Datei
            os.rename(doc_path, new_path)
            
            # Aktualisiere UI
            current_item = self.doc_list.currentItem()
            if current_item:
                current_item.setData(Qt.UserRole, new_path)
            self.status_label.setText(f"Dokument in {new_category} verschoben")
        
        except Exception as e:
            self.status_label.setText(f"Fehler beim Verschieben: {str(e)}")

    def get_document_category(self, doc_path):
        """Ermittele die Kategorie eines Dokuments"""

        parent_dir = os.path.basename(os.path.dirname(doc_path))
        if parent_dir in ["Rechnung", "Vertrag", "Mahnung", "Sonstiges"]:
            return parent_dir
        return "Sonstiges"
    
    def start_scan(self):
        """Startet den Scan-Prozess mit dem iPhone"""
        try:
            apple_script = '''
            tell application "Finder"
                activate
                open folder "Documents" of home
                delay 1
                tell application "System Events"
                    click at {200, 200} using {button 2}
                    delay 1
                    keystroke "i"
                    delay 1.5
                    keystroke "d"
                    delay 1
                end tell
            end tell
            '''
            
            self.status_label.setText("Starte Scan-Prozess...")
            subprocess.run(['osascript', '-e', apple_script])
            self.status_label.setText("Scan-Dialog geöffnet...")
        
        except Exception as e:
            self.status_label.setText(f"Fehler beim Scannen: {str(e)}")

    def process_accepted_document(self):
        """Verarbeitet ein akzeptiertes Dokument"""
        try:
            current_item = self.doc_list.currentItem()
            if current_item:
                doc_path = current_item.data(Qt.UserRole)
                if doc_path:
                    # Kategorie aus Combo-Box holen
                    category = self.category_combo.currentText()
                    # Dokument in die entsprechende Kategorie verschieben
                    self.update_document_category(doc_path, category)
                    self.status_label.setText("Dokument erfolgreich verarbeitet")
                else:
                    self.status_label.setText("Kein Dokumentenpfad gefunden")
            else:
                self.status_label.setText("Kein Dokument ausgewählt")
        except Exception as e:
            self.status_label.setText(f"Fehler bei der Verarbeitung: {str(e)}")

    def handle_rejected_document(self):
        """Behandelt abgelehnte Dokumente"""
        try:
            current_item = self.doc_list.currentItem()
            if current_item:
                doc_path = current_item.data(Qt.UserRole)
                if doc_path and os.path.exists(doc_path):
                    # Move to rejected folder
                    rejected_path = os.path.join(WATCHED_FOLDER, "Abgelehnt")
                    if not os.path.exists(rejected_path):
                        os.makedirs(rejected_path)
                    
                    new_path = os.path.join(rejected_path, os.path.basename(doc_path))
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(os.path.basename(doc_path))
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_path = os.path.join(rejected_path, f"{base}_{timestamp}{ext}")
                    
                    os.rename(doc_path, new_path)
                    
                    # Remove from list
                    row = self.doc_list.row(current_item)
                    self.doc_list.takeItem(row)
                    
                self.status_label.setText("Dokument wurde abgelehnt")
        except Exception as e:
            self.status_label.setText(f"Fehler beim Ablehnen: {str(e)}")

    def process_pending_document(self):
        """Verarbeitet das erste Dokument in der Liste nach ablauf des Timers"""
        self.sorting_timer.stop()
        if not self.pending_document or not self.pending_category:
            return
        
        try:
            doc_path = self.pending_document
            new_category = self.pending_category

            category_path = os.path.join(WATCHED_FOLDER, new_category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

            new_path = os.path.join(category_path, os.path.basename(doc_path))
            if os.path.exists(new_path):
                base, ext = ps.path.splitext(os.path.basename(doc_path))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = os.path.join(category_path, f"{base}_{timestamp}{ext}")

            os.rename(doc_path, new_path)

            log_message = f"{datetime.now().strftime('%H:%M:%S')} - {os.path.basename(doc_path)} -> {new_category}"
            self.log_list.insertItem(0, log_message)

            self.status_label.setText(f"Dokument in {new_category} verschoben")

        except Exception as e:
            self.status_label.setText(f"Fehler beim Verschieben: {str(e)}")
        
        finally:
            self.pending_document = None
            self.pending_category = None