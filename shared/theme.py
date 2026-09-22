import streamlit as st
import time
from pathlib import Path
from shared.ollama_client import test_ollama_connection

def get_current_theme():
    config_file = Path(".streamlit/config.toml")
    if config_file.exists():
        content = config_file.read_text().lower()
        if "light" in content: return "Light"
        if "dark" in content: return "Dark"
    return "System Default"

def set_theme(theme_choice):
    config_dir = Path(".streamlit")
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "config.toml"
    if theme_choice == "System Default":
        if config_file.exists(): config_file.unlink() 
    else:
        config_file.write_text(f'[theme]\nbase="{theme_choice.lower()}"\n')

def render_sidebar():
    st.sidebar.title("🤖 AI Services")
    if st.sidebar.button("Test Ollama Connection", use_container_width=True):
        success, msg = test_ollama_connection()
        if success:
            st.sidebar.success("Connected successfully!")
        else:
            st.sidebar.error(f"Cannot connect: {msg}")

    st.sidebar.divider()

    st.sidebar.title("⚙️ System Control")
    st.sidebar.subheader("App Appearance")
    current_theme = get_current_theme()
    theme_options = ["System Default", "Light", "Dark"]

    selected_theme = st.sidebar.radio(
        "Theme Preference", 
        theme_options, 
        index=theme_options.index(current_theme)
    )

    if selected_theme != current_theme:
        set_theme(selected_theme)
        time.sleep(0.2)
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Developer Toolkit v1.0\nRunning locally via pywebview.")