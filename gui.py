import sys
import threading
import os
from dataclasses import asdict
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QFileDialog, QCheckBox, QSpinBox, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# Import your scraping logic
from main import scrape_places, Place, save_places_to_xlsx, save_places_to_csv

class ScraperGUI(QWidget):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Google Maps Business Scraper')
        self.setGeometry(200, 200, 700, 600)
        self.set_dark_mode()
        self.set_custom_font()
        self.init_ui()
        self.log_signal.connect(self.log)

    def set_dark_mode(self):
        dark_stylesheet = """
        QWidget {
            background-color: #23272e;
            color: #e0e0e0;
            font-size: 15px;
        }
        QLineEdit, QTextEdit, QComboBox, QSpinBox {
            background-color: #2c313c;
            color: #e0e0e0;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton {
            background-color: #3b4252;
            color: #e0e0e0;
            border: 1px solid #5e81ac;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #5e81ac;
            color: #23272e;
        }
        QLabel {
            color: #e0e0e0;
            font-weight: 500;
        }
        QCheckBox {
            color: #e0e0e0;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background: #23272e;
            border: none;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def set_custom_font(self):
        font = QFont("Roboto", 11)
        QApplication.setFont(font)

    def init_ui(self):
        layout = QVBoxLayout()

        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel('Language:')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['English', 'Arabic', 'French', 'Deutsch'])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Category input
        cat_layout = QHBoxLayout()
        cat_label = QLabel('Categories (comma separated):')
        self.cat_input = QLineEdit()
        cat_layout.addWidget(cat_label)
        cat_layout.addWidget(self.cat_input)
        layout.addLayout(cat_layout)

        # Location input
        loc_layout = QHBoxLayout()
        self.loc_mode_combo = QComboBox()
        self.loc_mode_combo.addItems(['Country', 'City'])
        self.loc_input = QLineEdit()
        self.loc_input.setPlaceholderText('e.g. Morocco, Canada or Kenitra, Rabat')
        loc_layout.addWidget(QLabel('Search by:'))
        loc_layout.addWidget(self.loc_mode_combo)
        loc_layout.addWidget(self.loc_input)
        layout.addLayout(loc_layout)

        # Export type
        export_layout = QHBoxLayout()
        export_label = QLabel('Export type:')
        self.export_combo = QComboBox()
        self.export_combo.addItems(['Excel', 'JSON', 'HTML'])
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_combo)
        layout.addLayout(export_layout)

        # Number of results
        num_layout = QHBoxLayout()
        num_label = QLabel('Results per category:')
        self.num_spin = QSpinBox()
        self.num_spin.setMinimum(1)
        self.num_spin.setMaximum(1000)
        self.num_spin.setValue(10)
        num_layout.addWidget(num_label)
        num_layout.addWidget(self.num_spin)
        layout.addLayout(num_layout)

        # Headless mode
        self.headless_checkbox = QCheckBox('Run in background (faster, no browser window)')
        self.headless_checkbox.setChecked(True)
        layout.addWidget(self.headless_checkbox)

        # Output directory
        out_layout = QHBoxLayout()
        self.out_dir_input = QLineEdit('results')
        out_btn = QPushButton('Browse')
        out_btn.clicked.connect(self.browse_dir)
        out_layout.addWidget(QLabel('Output folder:'))
        out_layout.addWidget(self.out_dir_input)
        out_layout.addWidget(out_btn)
        layout.addLayout(out_layout)

        # Start button
        self.start_btn = QPushButton('Start Scraping')
        self.start_btn.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_btn)

        # Log/output area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def browse_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir_:
            self.out_dir_input.setText(dir_)

    def start_scraping(self):
        self.start_btn.setEnabled(False)
        self.log_area.clear()
        thread = threading.Thread(target=self.run_scraper)
        thread.start()

    def run_scraper(self):
        try:
            lang_map = {'English': 'en', 'Arabic': 'ar', 'French': 'fr', 'Deutsch': 'de'}
            lang_code = lang_map[self.lang_combo.currentText()]
            categories = [c.strip() for c in self.cat_input.text().split(',') if c.strip()]
            if not categories:
                self.log_signal.emit('Please enter at least one category.')
                self.start_btn.setEnabled(True)
                return
            locations = [l.strip() for l in self.loc_input.text().split(',') if l.strip()]
            if not locations:
                self.log_signal.emit('Please enter at least one location.')
                self.start_btn.setEnabled(True)
                return
            location_type = 'country' if self.loc_mode_combo.currentText() == 'Country' else 'city'
            export_type = self.export_combo.currentText().lower()
            total = self.num_spin.value()
            headless = self.headless_checkbox.isChecked()
            output_dir = self.out_dir_input.text().strip() or 'results'
            os.makedirs(output_dir, exist_ok=True)
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            jobs = [(cat, loc) for cat in categories for loc in locations]
            location_results = {}
            all_places = []
            for cat, loc in jobs:
                self.log_signal.emit(f'<b>Scraping: <span style="color:#5e81ac">{cat}</span> in <span style="color:#a3be8c">{loc}</span>...</b>')
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    import platform
                    if platform.system() == 'Windows':
                        browser_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                        browser = p.chromium.launch(executable_path=browser_path, headless=headless)
                    else:
                        browser = p.chromium.launch(headless=headless)
                    full_query = f"{cat} in {loc}"
                    scraped_count = 0
                    def progress_hook(place_name=None):
                        nonlocal scraped_count
                        scraped_count += 1
                        if place_name:
                            self.log_signal.emit(f'<span style="color:#b48ead">Scraped info about <b>{place_name}</b> ({scraped_count}/{total})</span>')
                        else:
                            self.log_signal.emit(f'<span style="color:#b48ead">Scraped {scraped_count}/{total}...</span>')
                    # Patch tqdm to call our hook with place name
                    import tqdm
                    orig_tqdm = tqdm.tqdm
                    def custom_tqdm(*args, **kwargs):
                        class DummyTqdm(orig_tqdm):
                            def update(self2, n=1, place_name=None):
                                super().update(n)
                                progress_hook(place_name)
                        return DummyTqdm(*args, **kwargs)
                    tqdm.tqdm = custom_tqdm
                    # Custom scrape_places to call progress_hook with name
                    def scrape_places_with_progress(*args, **kwargs):
                        places = []
                        for place in scrape_places(*args, **kwargs):
                            progress_hook(place.name)
                            places.append(place)
                        return places
                    places = scrape_places_with_progress(full_query, total, browser=browser, proxies=None)
                    tqdm.tqdm = orig_tqdm  # Restore
                    for place in places:
                        place.category = cat
                    location_results[loc] = places
                    all_places.extend(places)
                    browser.close()
            # Export
            if export_type == 'excel':
                output_path = os.path.join(output_dir, f"Maps_scrape_{'_'.join([l for l in locations])}_{timestamp}.xlsx")
                save_places_to_xlsx(all_places, output_path, append=False, lang_code=lang_code)
                self.log_signal.emit(f'<b>Results saved to <span style="color:#a3be8c">{output_path}</span></b>')
            elif export_type == 'json':
                import json
                output_path = os.path.join(output_dir, f"Maps_scrape_{'_'.join([l for l in locations])}_{timestamp}.json")
                export_list = []
                for location, places in location_results.items():
                    for place in places:
                        place_dict = asdict(place)
                        place_dict[location_type] = location
                        export_list.append(place_dict)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_list, f, ensure_ascii=False, indent=2)
                self.log_signal.emit(f'<b>Results saved to <span style="color:#a3be8c">{output_path}</span></b>')
            elif export_type == 'html':
                output_path = os.path.join(output_dir, f"Maps_scrape_{'_'.join([l for l in locations])}_{timestamp}.html")
                export_list = []
                for location, places in location_results.items():
                    for place in places:
                        place_dict = asdict(place)
                        place_dict[location_type] = location
                        export_list.append(place_dict)
                df = pd.DataFrame(export_list)
                df.to_html(output_path, index=False, border=1, justify='center')
                self.log_signal.emit(f'<b>Results saved to <span style="color:#a3be8c">{output_path}</span></b>')
            else:
                self.log_signal.emit('Unknown export type.')
            # Show summary
            self.log_signal.emit('<br><b>==============================<br>         SUMMARY<br>==============================</b>')
            idx = 1
            for place in all_places:
                summary = (
                    f'<pre style="font-family:Roboto,monospace;font-size:13px;">  {idx}. {place.name}\n'
                    f'     Address: {place.address}\n'
                    f'     Website: {place.website}\n'
                    f'     Phone: {place.phone_number}\n'
                    f'     Reviews: {place.reviews_count} (Avg: {place.reviews_average})\n'
                    f'     Category: {place.category}\n'
                    f'     Social: {place.social_media_urls}\n'
                    f'     Email: {place.email}\n'
                    f'     Latitude: {place.latitude}\n'
                    f'     Longitude: {place.longitude}\n'
                    f'     Weekly Hours: {place.weekly_hours}\n'
                    f'     Tags: {place.tags}\n'
                    f'     Introduction: {place.introduction}\n     ---</pre>'
                )
                self.log_signal.emit(summary)
                idx += 1
            self.log_signal.emit('<b>==============================</b>')
            self.log_signal.emit('<b>Scraping complete!</b>')
        except Exception as e:
            self.log_signal.emit(f'<span style="color:#bf616a">Error: {e}</span>')
        self.start_btn.setEnabled(True)

    def log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ScraperGUI()
    gui.show()
    sys.exit(app.exec_())
