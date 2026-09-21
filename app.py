"""Drag-and-drop file-to-Markdown converter using MarkItDown + Streamlit."""

import os
import tempfile

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(page_title="MarkItDown Web", page_icon="⚡", layout="centered")

# Custom CSS for a modern, sleek aesthetic
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Title styling */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 2rem;
    }
    
    .hero-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 3rem;
    }

    /* Style the convert button */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        border: none;
        color: white;
    }
    
    /* Style the text area */
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #475569;
        font-family: 'JetBrains Mono', 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

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

# UI Layout
st.markdown('<div class="hero-title">MarkItDown ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Transform your files into clean, beautiful Markdown instantly.</div>', unsafe_allow_html=True)

st.write("") # Spacer

with st.container():
    uploaded_files = st.file_uploader(
        "Upload files or drag and drop", 
        accept_multiple_files=True,
        help="Supported formats: Word, Excel, PowerPoint, PDF, Images, Audio, HTML, CSV, JSON, XML"
    )

st.write("") # Spacer

if uploaded_files:
    # Use columns to center the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        convert_pressed = st.button("✨ Convert to Markdown", use_container_width=True)

    if convert_pressed:
        combined_parts = []
        download_paths = []
        output_dir = tempfile.mkdtemp(prefix="markitdown_")
        
        st.write("---")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            stem = os.path.splitext(filename)[0]
            status_text.text(f"Converting {filename}...")
            
            temp_input_path = os.path.join(output_dir, filename)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                result = md_converter.convert(temp_input_path)
                markdown_text = _extract_markdown(result)
            except Exception as exc:  # noqa: BLE001
                markdown_text = f"**Error converting `{filename}`:** {exc}"
                combined_parts.append(f"## {filename}\n\n{markdown_text}\n")
                continue

            combined_parts.append(f"## {filename}\n\n{markdown_text}\n")

            out_path = os.path.join(output_dir, f"{stem}.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            download_paths.append(out_path)
            
            progress_bar.progress((idx + 1) / len(uploaded_files))

        status_text.empty()
        progress_bar.empty()
        
        combined_markdown = "\n---\n\n".join(combined_parts)
        st.toast("Conversion complete! 🎉", icon="✅")
        
        # Results area
        st.markdown("### 📄 Results")
        
        # Display the result in a styled container
        st.text_area("Preview", value=combined_markdown, height=400, label_visibility="collapsed")
        
        if download_paths:
            st.markdown("### 📥 Download")
            # Display downloads in columns
            num_cols = min(3, len(download_paths))
            if num_cols > 0:
                dl_cols = st.columns(num_cols)
                
                for i, file_path in enumerate(download_paths):
                    file_name = os.path.basename(file_path)
                    with open(file_path, "rb") as file:
                        with dl_cols[i % num_cols]:
                            st.download_button(
                                label=f"⬇️ {file_name}",
                                data=file,
                                file_name=file_name,
                                mime="text/markdown",
                                key=file_path,
                                use_container_width=True
                            )
