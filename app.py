"""Drag-and-drop file-to-Markdown converter using MarkItDown + Streamlit."""

import os
import tempfile

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(page_title="MarkItDown Web", page_icon="📝")

# Reuse a single MarkItDown instance across conversions.
@st.cache_resource
def get_md_converter():
    return MarkItDown()

md_converter = get_md_converter()

def _extract_markdown(result) -> str:
    """MarkItDown's result object exposes different attributes across versions."""
    if hasattr(result, "text_content") and result.text_content is not None:
        return result.text_content
    if hasattr(result, "markdown") and result.markdown is not None:
        return result.markdown
    raise AttributeError("MarkItDown result has neither 'text_content' nor 'markdown'")

st.title("MarkItDown Web")
st.markdown("Drag and drop files below to convert them to Markdown.")

uploaded_files = st.file_uploader(
    "Drop files here", 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Convert to Markdown", type="primary"):
        combined_parts = []
        download_paths = []
        output_dir = tempfile.mkdtemp(prefix="markitdown_")

        with st.spinner("Converting files..."):
            for uploaded_file in uploaded_files:
                filename = uploaded_file.name
                stem = os.path.splitext(filename)[0]
                
                # Streamlit uploaded files are UploadedFile objects.
                # It's safest to write the uploaded file to a temporary location first, 
                # as MarkItDown's internal parsers might expect a file path.
                temp_input_path = os.path.join(output_dir, filename)
                with open(temp_input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                try:
                    result = md_converter.convert(temp_input_path)
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
        
        st.success("Conversion complete!")
        
        st.subheader("Combined Markdown")
        st.text_area("Markdown Output", value=combined_markdown, height=400, label_visibility="collapsed")
        
        st.subheader("Download converted .md files")
        for file_path in download_paths:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"Download {file_name}",
                    data=file,
                    file_name=file_name,
                    mime="text/markdown",
                    key=file_path
                )
