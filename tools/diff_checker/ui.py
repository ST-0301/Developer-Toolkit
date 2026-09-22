import difflib
import json
import streamlit as st
import streamlit.components.v1 as components
import time
from shared.analytics import log_usage
from tools.diff_checker.services import preprocess_text, get_diff_stats, generate_monaco_diff_html

def render(navigate_to):
    # Header & Navigation
    col_title, col_nav = st.columns([8, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: -20px;'>Code Difference Checker</h1>", unsafe_allow_html=True)
    with col_nav:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="back_diff"):
            navigate_to("Home")
        
    st.divider()

    # Allowed file types for drag and drop
    allowed_types = ["cs", "cshtml", "txt", "py"]

    col_orig, col_upd = st.columns(2)
    
    with col_orig:
        st.markdown("**Original Code**")
        orig_file = st.file_uploader("Upload original file", type=allowed_types, key="orig_file", label_visibility="collapsed")
        
        # If a file is dropped/uploaded, read its content into session state
        if orig_file is not None:
            st.session_state["orig_code"] = orig_file.read().decode("utf-8")
            
        original_text = st.text_area("Original Code Text", height=250, key="orig_code", label_visibility="collapsed")

    with col_upd:
        st.markdown("**Updated Code**")
        upd_file = st.file_uploader("Upload updated file", type=allowed_types, key="upd_file", label_visibility="collapsed")
        
        # If a file is dropped/uploaded, read its content into session state
        if upd_file is not None:
            st.session_state["upd_code"] = upd_file.read().decode("utf-8")
            
        updated_text = st.text_area("Updated Code Text", height=250, key="upd_code", label_visibility="collapsed")

    # Filters & Actions Layout Adjusted
    col_filters, col_theme, col_blank, col_btn = st.columns([2, 2, 1.5, 2])

    with col_filters:
        st.markdown("**Noise Reduction**")
        ignore_blank = st.checkbox("Ignore blank lines", value=True)
        ignore_case = st.checkbox("Ignore casing", value=False)
            
    with col_theme:
        st.markdown("**Editor Theme**")
        editor_theme = st.selectbox(
            "Theme", 
            ["Light (VS)", "Dark (VS Code)"], 
            label_visibility="collapsed"
        )
        monaco_theme = "vs-dark" if "Dark" in editor_theme else "vs"

    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        compare_clicked = st.button("Compare Code", type="primary", use_container_width=True)

    if compare_clicked:
        if not original_text and not updated_text:
            st.warning("Please paste code or upload files into both boxes to compare.")
        else:
            start_total = time.perf_counter()

            orig_processed = preprocess_text(original_text, ignore_blank, ignore_case)
            upd_processed = preprocess_text(updated_text, ignore_blank, ignore_case)

            added, removed, modified, sim = get_diff_stats(orig_processed, upd_processed)
            html_diff = generate_monaco_diff_html(orig_processed, upd_processed, theme=monaco_theme)
            
            total_duration = int((time.perf_counter() - start_total) * 1000)
            
            log_usage(
                "Diff Checker", 
                "Compare Code", 
                total_duration_ms=total_duration,
                metadata=f"Similarity: {sim}%"
            )
            st.session_state["diff_stats"] = (added, removed, modified, sim)
            st.session_state["diff_html"] = html_diff

    # Results Display
    if "diff_html" in st.session_state:
        st.divider()
        st.subheader("Comparison Results")
        
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        added, removed, modified, sim = st.session_state["diff_stats"]
        s_col1.metric("Lines Added", added)
        s_col2.metric("Lines Removed", removed)
        s_col3.metric("Lines Modified", modified)
        s_col4.metric("Similarity", f"{sim}%")
        
        st.write("")
        
        with st.container(border=True):
            components.html(st.session_state["diff_html"], height=600, scrolling=False)