import streamlit as st
from shared.database import initialize_database
from shared.theme import render_sidebar
from tools.analytics.ui import render_dashboard
from tools.journal import ui as journal_ui
from tools.formatter import ui as formatter_ui
from tools.translator import ui as translator_ui
from tools.diff_checker import ui as diff_checker_ui

# ==========================================
# INITIALIZATION & APP SETUP
# ==========================================
st.set_page_config(
    page_title="Developer Toolkit", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
initialize_database()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def navigate_to(page_name):
    """Handles page routing"""
    st.session_state.current_page = page_name
    st.rerun()

# Render Global Sidebar
render_sidebar()

# ==========================================
# ROUTER
# ==========================================
if st.session_state.current_page == "Home":
    st.title("Developer Toolkit")
    render_dashboard()
    st.divider()
    st.markdown("### 🛠️ Available Tools")
    st.write("") 
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        with st.container(border=True):
            st.markdown("### 📝 Daily Journal")
            st.markdown("🚧 *Under Construction* - Automate engineering work logs using local AI models.")
            st.write("")
            st.button("Under Construction", key="btn_journal", use_container_width=True, disabled=True)

    with row1_col2:
        with st.container(border=True):
            st.markdown("### 📄 Code Formatter")
            st.markdown("Batch format local code files for AI web chat prompts.")
            st.write("")
            if st.button("Launch Tool", key="btn_formatter", use_container_width=True, type="primary"):
                navigate_to("Formatter")
                
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        with st.container(border=True):
            st.markdown("### 💬 Communication Translator")
            st.markdown("🚧 *Under Construction* - Transform raw thoughts into professional workplace communication.")
            st.write("")
            st.button("Under Construction", key="btn_translator", use_container_width=True, disabled=True)

    with row2_col2:
        with st.container(border=True):
            st.markdown("### 🔍 Code Difference Checker")
            st.markdown("Compare code side-by-side with formatting noise reduction and statistics.")
            st.write("")
            if st.button("Launch Tool", key="btn_diffchecker", use_container_width=True, type="primary"):
                navigate_to("DiffChecker")

elif st.session_state.current_page == "Journal":
    journal_ui.render(navigate_to)

elif st.session_state.current_page == "Formatter":
    formatter_ui.render(navigate_to)

elif st.session_state.current_page == "Translator":
    translator_ui.render(navigate_to)

elif st.session_state.current_page == "DiffChecker":
    diff_checker_ui.render(navigate_to)