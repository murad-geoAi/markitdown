"""Drag-and-drop file-to-Markdown converter using MarkItDown + Gradio."""

import os
import tempfile

import gradio as gr
from markitdown import MarkItDown

# Reuse a single MarkItDown instance across conversions.
md_converter = MarkItDown()


def _extract_markdown(result) -> str:
    """MarkItDown's result object exposes different attributes across versions."""
    if hasattr(result, "text_content") and result.text_content is not None:
        return result.text_content
    if hasattr(result, "markdown") and result.markdown is not None:
        return result.markdown
    raise AttributeError("MarkItDown result has neither 'text_content' nor 'markdown'")


def convert_files(files):
    """Convert each uploaded file to Markdown, isolating per-file failures."""
    if not files:
        return "No files uploaded.", []

    combined_parts = []
    download_paths = []
    output_dir = tempfile.mkdtemp(prefix="markitdown_")

    for file_path in files:
        filename = os.path.basename(file_path)
        stem = os.path.splitext(filename)[0]

        try:
            result = md_converter.convert(file_path)
            markdown_text = _extract_markdown(result)
        except Exception as exc:  # noqa: BLE001 - one bad file shouldn't stop the batch
            markdown_text = f"**Error converting `{filename}`:** {exc}"
            combined_parts.append(f"## {filename}\n\n{markdown_text}\n")
            continue

        combined_parts.append(f"## {filename}\n\n{markdown_text}\n")

        out_path = os.path.join(output_dir, f"{stem}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        download_paths.append(out_path)

    combined_markdown = "\n---\n\n".join(combined_parts)
    return combined_markdown, download_paths


with gr.Blocks(title="MarkItDown Web") as demo:
    gr.Markdown("# MarkItDown Web\nDrag and drop files below to convert them to Markdown.")

    file_input = gr.File(
        label="Drop files here",
        file_count="multiple",
        type="filepath",
    )

    convert_btn = gr.Button("Convert to Markdown", variant="primary")

    output_markdown = gr.Textbox(
        label="Combined Markdown",
        lines=20,
        buttons=["copy"],
    )

    output_files = gr.File(
        label="Download converted .md files",
        file_count="multiple",
    )

    convert_btn.click(
        fn=convert_files,
        inputs=[file_input],
        outputs=[output_markdown, output_files],
    )

if __name__ == "__main__":
    demo.launch()
