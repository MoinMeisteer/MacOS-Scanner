import sys
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gui.main_window import MainWindow
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from scanner.document_processor import DocumentProcessor
from config.settings import WATCHED_FOLDER


class DocumentHandler(FileSystemEventHandler):
    def __init__(self, window):
        super().__init__()
        self.processor = DocumentProcessor()
        self.window = window

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.jpg', '.png', '.jpeg', '.heic', '.pdf')):
            logging.info(f"Neues Dokument erkannt: {event.src_path}")
            self.window.status_label.setText(f"Verarbeite {os.path.basename(event.src_path)}...")
            
            # Create item first, then add it to the list
            item = QListWidgetItem(os.path.basename(event.src_path))
            item.setData(Qt.UserRole, event.src_path)
            self.window.doc_list.addItem(item)
            
            # Process the document
            try:
                self.processor.process_document(event.src_path)
                logging.info(f"Dokument verarbeitet: {os.path.basename(event.src_path)}")
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung: {str(e)}")
                self.window.status_label.setText(f"Fehler: {str(e)}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    if not os.path.exists(WATCHED_FOLDER):
        logging.error(f"Überwachter Ordner existiert nicht: {WATCHED_FOLDER}")
        os.makedirs(WATCHED_FOLDER)
        logging.info(f"Ordner wurde erstellt: {WATCHED_FOLDER}")

    handler = DocumentHandler(window)
    observer = Observer()
    observer.schedule(handler, WATCHED_FOLDER, recursive=False)
    observer.start()

    logging.info(f"Überwache Ordner: {WATCHED_FOLDER}")
    logging.info("Warte auf neue Dokumente...")

    try:
        return app.exec_()
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Programm beendet")
        observer.join()


if __name__ == "__main__":
    sys.exit(main())