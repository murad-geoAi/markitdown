# MarkItDown Web

A small drag-and-drop web app that converts files to Markdown using
Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) library,
with a [Gradio](https://www.gradio.app/) interface.

This project does not fork or copy MarkItDown's source — it depends on the
published `markitdown` package on PyPI.

## Setup

1. Create and activate a virtual environment (Python 3.10+):

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run the web app

```bash
python app.py
```

Gradio will print a local URL (e.g. `http://127.0.0.1:7860`). Open it in
your browser, drag one or more files onto the upload area, and click
**Convert to Markdown**. You'll get the combined Markdown in a textbox
(with a copy button) and a downloadable `.md` file for each input file.

## Terminal alternative

You don't need the web app to convert a single file — MarkItDown also
ships a CLI:

```bash
markitdown file.pdf -o file.md
```
