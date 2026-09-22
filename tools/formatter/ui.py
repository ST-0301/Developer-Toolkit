import streamlit as st
import time
from shared.analytics import log_usage
from tools.formatter.services import process_code_files_from_paths

def render(navigate_to):
    if "formatter_text_key" not in st.session_state:
        st.session_state.formatter_text_key = 1

    # Header & Navigation
    col_title, col_nav = st.columns([8, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: -20px;'>Code Formatter</h1>", unsafe_allow_html=True)
    with col_nav:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="back_formatter"):
            navigate_to("Home")
        
    st.divider()

    st.markdown("Paste absolute file paths below (one per line). They will be merged, separated by headers containing their full path, and prepared for copying into LLM chat windows.")
    st.caption("Pro-tip: Highlight multiple files in VS Code or File Explorer and use 'Copy Path'.")
    
    paths_input = st.text_area(
        "File Paths", 
        height=150, 
        placeholder="C:\\Users\\804793\\Projects\\DeveloperToolkit\\app.py\nC:\\Users\\804793\\Projects\\DeveloperToolkit\\desktop_app.py",
        label_visibility="collapsed",
        key=f"paths_input_{st.session_state.formatter_text_key}"
    )

    col_format, col_clear, col_empty = st.columns([2, 2, 6]) 
    
    with col_format:
        format_clicked = st.button("Format Files", type="primary", use_container_width=True)
        
    with col_clear:
        if st.button("Clear List", use_container_width=True):
            st.session_state.formatter_text_key += 1
            st.rerun()

    if format_clicked:
        if paths_input.strip():
            start_total = time.perf_counter()
            formatted_output, count = process_code_files_from_paths(paths_input)
            total_duration = int((time.perf_counter() - start_total) * 1000)

            log_usage(
                "Formatter", 
                "Format Files", 
                total_duration_ms=total_duration,
                metadata=f"Files: {count}"
            )
            st.success(f"Successfully processed {count} file(s).")
            st.markdown("**Formatted Output:** *(Hover over the top right corner of the box below to click the **Copy** icon)*")
            st.code(formatted_output, language="text")
        else:
            st.warning("Please paste at least one file path.")