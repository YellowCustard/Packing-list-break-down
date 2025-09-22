diff --git a/README.md b/README.md
index 9008800d3c7b7c7ff271d6b75aa25fecbfb14243..b608e4c8e8287806b0a254214dfeed8c54173d71 100644
--- a/README.md
+++ b/README.md
@@ -1,7 +1,70 @@
+# Packing List Translator
+
+Translate the contents of Excel spreadsheets into English (or any other language
+supported by Google Translate) and export the result as a new workbook. The
+command-line application imports an `.xlsx` file, detects the language in each
+cell, and writes a translated version of every sheet.
+
+## Features
+
+- Import any `.xlsx` workbook with one or multiple sheets.
+- Automatically detect the language used in each cell and translate it to the
+  target language (English by default).
+- Skip numbers, formulas, and empty cells to keep your data intact.
+- Export the translated workbook while preserving sheet names and merged cells.
+
+## Requirements
+
+- Python 3.10+
+- An internet connection to access the Google Translate service used by the
+  [`googletrans`](https://pypi.org/project/googletrans/) library.
+
+## Installation
+
+Create and activate a virtual environment, then install the project and its
+command-line entry point:
+
+```bash
+python -m venv .venv
+source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
+pip install .
+```
+
+For development (including running the unit tests) install the optional extras:
+
+```bash
+pip install .[dev]
+```
+
+## Usage
+
+Run the `translate-excel` command with the path to the source workbook and the
+desired output location:
+
+```bash
+translate-excel path/to/source.xlsx path/to/translated.xlsx
+```
+
+Optional flags allow you to customise the translation:
+
+- `--source`: Language code to translate from (default: automatic detection).
+- `--target`: Language code to translate into (default: `en`).
+- `--batch-size`: Number of cells translated per request (default: `25`).
+
+Example translating from Spanish to English and saving the result next to the
+original file:
+
+```bash
+translate-excel data/spanish.xlsx data/spanish-translated.xlsx --target en
+```
+
+## Running Tests
+
+Install the development dependencies and execute:
+
+```bash
+pytest
+```
+
+The tests use a stub translator so they run offline without contacting external
+services.
