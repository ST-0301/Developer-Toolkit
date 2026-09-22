import streamlit as st
import time
from pathlib import Path
from datetime import datetime
from shared.analytics import log_usage
from shared.settings import get_settings, save_settings
from shared.ollama_client import summarize_chunk, generate_journal
from tools.journal.services import split_into_chunks, save_journal_to_db

def render(navigate_to):
    # Header & Navigation
    col_title, col_nav = st.columns([8, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: -20px;'>Daily Journal Generator</h1>", unsafe_allow_html=True)
    with col_nav:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="back_journal"):
            navigate_to("Home")
        
    st.divider()

    settings = get_settings()
    saved_prompt = settings[0] if settings else ""
    saved_onedrive = settings[1] if settings else ""
    saved_fast_model = settings[2] if settings else "fast-summarizer"
    saved_final_model = settings[3] if settings else "qwen2.5:7b"

    if not saved_prompt:
        DEFAULT_PROMPT_FILE = Path("tools/journal/default_prompt.txt")
        if DEFAULT_PROMPT_FILE.exists():
            saved_prompt = DEFAULT_PROMPT_FILE.read_text(encoding="utf-8")
        else:
            saved_prompt = "You are generating a professional engineering work journal."

    with st.expander("Tool Settings", expanded=False):
        st.markdown("**Model & Path Configuration**")
        col_a, col_b = st.columns(2)
        with col_a:
            fast_model_name = st.text_input("Fast Summarizer Model", value=saved_fast_model)
            onedrive_path = st.text_input("OneDrive Folder Path", value=saved_onedrive)
        with col_b:
            final_model_name = st.text_input("Final Journal Model", value=saved_final_model)
            
        prompt = st.text_area("System Prompt", value=saved_prompt, height=150)

        if st.button("Save Settings", type="primary"):
            save_settings(prompt, onedrive_path, fast_model_name, final_model_name)
            st.toast("Settings saved successfully!")

    st.subheader("Process Work Context")
    uploaded_context_file = st.file_uploader("Upload Daily Context File", type=["md", "txt"], key="journal_uploader")

    if uploaded_context_file:
        content = uploaded_context_file.read().decode("utf-8")
        lines_count = len(content.splitlines())
        char_count = len(content)
        st.info(f"**File Stats:** {lines_count:,} Lines | {char_count:,} Characters")
        
        if st.button("Generate Journal", type="primary"):
            if not fast_model_name or not final_model_name:
                st.error("Please configure the Ollama Models in the Tool Settings above.")
            else:
                try:
                    start_total = time.perf_counter()
                    start_preprocess = time.perf_counter()

                    chunks = split_into_chunks(content, max_chars=4000)
                    final_context = content
                    
                    if len(chunks) > 1:
                        st.warning(f"Large document detected. Splitting into {len(chunks)} chunks for preprocessing...")
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        merged_summaries = []
                        
                        for i, chunk in enumerate(chunks):
                            progress_text.text(f"Summarizing chunk {i+1} of {len(chunks)} with {fast_model_name}...")
                            chunk_summary = summarize_chunk(fast_model_name, chunk)
                            merged_summaries.append(f"--- Chunk {i+1} Summary ---\n{chunk_summary}")
                            progress_bar.progress((i + 1) / len(chunks))
                        
                        progress_text.text("Merging summaries...")
                        final_context = "\n\n".join(merged_summaries)
                        st.success("Document preprocessing complete!")

                    preprocess_duration = int((time.perf_counter() - start_preprocess) * 1000)

                    with st.spinner(f"Generating final structured journal using {final_model_name}..."):
                        start_ai = time.perf_counter()
                        journal = generate_journal(final_model_name, prompt, final_context)
                        ai_duration = int((time.perf_counter() - start_ai) * 1000)

                        start_post = time.perf_counter()
                        st.session_state["journal"] = journal
                        save_journal_to_db(uploaded_context_file.name, journal)

                        postprocess_duration = int((time.perf_counter() - start_post) * 1000)
                        total_duration = int((time.perf_counter() - start_total) * 1000)
                        
                        log_usage(
                            "Journal", 
                            "Generate Journal",
                            total_duration_ms=total_duration,
                            preprocess_duration_ms=preprocess_duration,
                            ai_duration_ms=ai_duration,
                            postprocess_duration_ms=postprocess_duration,
                            model_name=final_model_name,
                            input_size=char_count,
                            output_size=len(journal)
                        )
                        st.toast("Journal generated and saved to DB history!")
                        
                except Exception as e:
                    st.error(f"Generation Failed: {str(e)}")

        if "journal" in st.session_state:
            st.subheader("Result output")
            st.text_area("Generated Markdown", st.session_state["journal"], height=400)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Save To OneDrive"):
                    if not onedrive_path:
                        st.error("Please configure the OneDrive Folder path in Settings.")
                    else:
                        try:
                            save_folder = Path(onedrive_path)
                            save_folder.mkdir(parents=True, exist_ok=True)
                            filename = datetime.now().strftime("%Y-%m-%d") + ".md"
                            output_file = save_folder / filename
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(st.session_state["journal"])
                            st.success(f"Saved to {output_file}")
                        except Exception as e:
                            st.error(f"Failed to save to OneDrive: {str(e)}")
            with col2:
                download_filename = datetime.now().strftime("%Y-%m-%d_journal") + ".md"
                st.download_button(
                    label="Download Local Copy",
                    data=st.session_state["journal"],
                    file_name=download_filename,
                    mime="text/markdown"
                )