# Google Maps Business Scraper

<p align="center">
  <img src="banner.webp" alt="Google Maps Business Scraper Banner" width="80%">
</p>

A powerful, multi-language Google Maps business scraping tool that extracts comprehensive business information and exports it in your preferred language and format. This script supports English, Arabic, French, and Deutsch, and is designed for clean, user-friendly exports to Excel, JSON, or HTML.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Notes](#notes)
- [Contributing](#contributing)
- [Planned & Suggested Features](#planned--suggested-features)

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed (for Playwright)
- Internet connection

## Key Features

- Multi-language CLI and export (English, Arabic, French, Deutsch)
- Extracts all business info: name, address, phone, website, email, reviews, tags/categories, weekly hours, geolocation, social media, and more
- Exports to Excel (with clickable links), JSON, or HTML
- Progress bar, error logging, and proxy support
- Clean, translated headers in all exports
- Always uses the correct Google Maps language (`hl` parameter)
- Option to show or hide browser during scraping
- Removes unused code and keeps exports clean

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

Run the script from the command line:

```bash
python main.py
```

- Follow the prompts to select language, categories, location, export type, and number of results.
- Choose whether to show the browser or run in headless mode.
- Results will be saved in the `results/` folder.

## Example

- Search for "Restaurants" in "Kenitra" and export 10 results to Excel in French:
  1. Choose French as the language
  2. Enter "Restaurants" as the category
  3. Enter "Kenitra" as the city
  4. Choose Excel as the export type
  5. Enter 10 for number of results
  6. Choose browser visibility

## Notes

- For Arabic, terminal output may appear disconnected or reversed; use Windows Terminal or a GUI for best results.
- All exported URLs (maps, website, social media) are clickable in Excel.
- If you encounter issues with Playwright, ensure Chrome is installed and run `playwright install`.
- Error logs are saved to `scrape_errors.log`.

## Contributing

Contributions are welcome! If you have ideas, bug fixes, or want to add new features, please open an issue or submit a pull request. For major changes, please discuss them first to ensure smooth integration.

## Planned & Suggested Features

- **Database Integration:** Save scraped data directly to SQLite, PostgreSQL, or MySQL databases for advanced querying and analytics.
- **REST API:** Expose scraping and data access via a secure API for integration with other tools and automation workflows.
- **Graphical User Interface (GUI):** User-friendly desktop app for non-technical users, with drag-and-drop and visual controls.
- **Advanced Filtering:** Filter results by rating, open hours, or specific tags before export.
- **Cloud Deployment:** Run the scraper on cloud platforms with scheduled jobs and remote access.

If you are interested in helping with any of these features, please reach out or start a discussion!
