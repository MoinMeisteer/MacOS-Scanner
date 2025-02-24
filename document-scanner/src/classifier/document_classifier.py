import logging
import re
from datetime import datetime
from transformers import pipeline
import json

class DocumentClassifier:
    def __init__(self):
        try:
            self.categories = ["Rechnungen", "Verträge", "Bescheinigungen", "Sonstiges"]
            
            # Load pre-trained BART model for zero-shot classification
            self.nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        except Exception as e:
            logging.error(f"Fehler beim Initialisieren des Dokumentenklassifizierers: {str(e)}")
            raise

    def classify(self, text):
        try:
            text = text.lower()
            
            # Define candidate labels for classification
            candidate_labels = self.categories
            
            # Use the model to classify the text
            result = self.nlp(text, candidate_labels)
            category = result['labels'][0]
            
            suggested_filename = self.generate_filename(text, category)

            return category, suggested_filename
                
        except Exception as e:
            logging.error(f"Klassifizierung fehlgeschlagen: {str(e)}")
            return "Sonstiges", None

    def detect_sender(self, text):
        try:
            # Define candidate labels for sender detection
            candidate_labels = ["Telekom", "Vodafone", "1&1", "O2", "E.ON", "RWE", "EnBW", "EWE", "Stadtwerke", "Amazon", "eBay", "PayPal", "Apple", "Google", "Microsoft", "Facebook", "Twitter", "Instagram", "WhatsApp", "Signal", "Telegram", "Threema", "Postbank", "Commerzbank", "Deutsche Bank", "ING", "Sparkasse", "Volksbank", "DKB", "N26", "Revolut", "Fidor", "HypoVereinsbank", "Consorsbank", "Deutsche Kreditbank", "Deutsche Bahn", "Lufthansa", "Airbus", "BMW", "Mercedes", "Volkswagen", "Audi", "Porsche", "Opel", "Ford", "Renault", "Peugeot", "Citroën", "Fiat", "Toyota", "Nissan", "Honda", "Mazda", "Subaru", "Mitsubishi", "Bundesagentur für Arbeit", "Jobcenters", "Arbeitsamt", "Finanzamt", "Stadtverwaltung", "Polizei", "Feuerwehr", "Rotes Kreuz", "Malteser", "Johanniter", "DRK", "THW", "ADAC", "Allianz", "HUK-Coburg", "DEVK", "AOK", "Barmer"]
            
            # Use the model to detect the sender
            result = self.nlp(text, candidate_labels)
            sender = result['labels'][0]
            
            return sender
        except Exception as e:
            logging.error(f"Fehler bei der Sendererkennung: {str(e)}")
            return "Unbekannt"
    
    def detect_date(self, text):
        """Versucht ein Datum im Text zu finden."""
        date_patterns = [
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{2}/\d{2}/\d{4}',    # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',    # DD-MM-YYYY
            r'\d{1,2}\.\s?\d{1,2}\.\s?\d{4}',  # D.M.YYYY or DD. MM. YYYY
            r'\d{1,2}\.\s?\d{1,2}\.\s?\d{2}',  # DD.MM.YY
            r'\d{4}-\d{2}-\d{2}'     # YYYY-MM-DD (ISO format)
        ]

        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            dates = [match.group(0) for match in matches]
            if dates:
                return self._normalize_date(dates[0])
            
        return datetime.now().strftime("%d.%m.%Y")
    
    def detect_amount(self, text):
        """Erkennt Beträge im Text."""
        # Verschiedene Betragsmuster (z.B. 1.234,56 € oder EUR 1.234,56)
        amount_patterns = [
            r'(\d+[.,]\d{2})\s*[€€EUR]',
            r'[€€EUR]\s*(\d+[.,]\d{2})',
            r'(\d+[.,]\d{2})\s*Euro',
            r'Euro\s*(\d+[.,]\d{2})',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    
    def _normalize_date(self, date_str):
        """Konvertiert verschiedene Datumsformate in DD.MM.YYYY"""

        try:
            date_str = date_str.replace("/", "")

            for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%y"):
                try:
                    return datetime.strptime(date_str, fmt).strftime("%d.%m.%Y")
                except ValueError:
                    continue
                return date_str
        except Exception as e:
            logging.error(f"Fehler beim Normalisieren des Datums: {str(e)}")
            return datetime.now().strftime("%d.%m.%Y")
    
    def generate_filename(self, text, category):
        """Generates a filename based on sender, date, amount and category."""
        try:
            sender = self.detect_sender(text)
            date = self.detect_date(text)
            doc_type = self.detect_document_type(text)
            amount = self.detect_amount(text)
            
            # Remove invalid characters
            safe_sender = re.sub(r'[<>:"/\\|?*]', '', sender)
            
            # Build filename components
            components = [date, safe_sender]
            
            if amount:
                components.append(f"{amount}EUR")
            
            if doc_type != "Sonstiges":
                components.append(doc_type)
                
            components.append(category)
            
            # Create filename
            filename = " - ".join(components)
            return filename.strip()
            
        except Exception as e:
            logging.error(f"Fehler bei der Dateinamensgenerierung: {str(e)}")
            return "Unbenannt"
            
    def detect_document_type(self, text):
        """Erkennt den Dokumententyp basierend auf Schlüsselwörtern."""
        text = text.lower()
        
        type_patterns = {
            'Rechnung': [
                r'rechnung(?:s-?nummer)?[\s:]*([\w\d-]+)',
                r'rechnungs?betrag',
                r'zahlung(?:s-?eingang)?',
            ],
            'Mahnung': [
                r'mahnung',
                r'zahlungserinnerung',
                r'letzte\s+mahnung',
            ],
            'Vertrag': [
                r'vertrag(?:s-?nummer)?[\s:]*([\w\d-]+)',
                r'versicherungsschein',
                r'versicherungs-?nummer',
            ],
            'Bescheinigung': [
                r'bescheinigung',
                r'zertifikat',
                r'nachweis',
            ]
        }
        
        for doc_type, patterns in type_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                return doc_type
        
        return "Sonstiges"
    
    def classify(self, text):
        try:
            text = text.lower()
            
            # Enhanced keyword lists for better classification
            rechnung_keywords = ['rechnung', 'betrag', 'zahlung', 'euro', '€', 'summe', 'preis']
            vertrag_keywords = ['vertrag', 'vereinbarung', 'bedingungen', 'laufzeit', 'kündigung']
            bescheinigung_keywords = ['bescheinigung', 'bestätigung', 'nachweis', 'zertifikat']
            
            if any(word in text for word in rechnung_keywords):
                category = "Rechnungen"
            elif any(word in text for word in vertrag_keywords):
                category = "Verträge"
            elif any(word in text for word in bescheinigung_keywords):
                category = "Bescheinigungen"
            else:
                category = "Sonstiges"
            
            suggested_filename = self.generate_filename(text, category)

            return category, suggested_filename
                
        except Exception as e:
            logging.error(f"Klassifizierung fehlgeschlagen: {str(e)}")
            return "Sonstiges", None
    
    