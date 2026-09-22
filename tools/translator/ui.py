import streamlit as st
import time
from pathlib import Path
from shared.analytics import log_usage
from shared.ollama_client import translate_message

def render(navigate_to):
    if "translator_text_key" not in st.session_state:
        st.session_state.translator_text_key = 1

    # Header & Navigation
    col_title, col_nav = st.columns([8, 1])
    with col_title:
        st.markdown("<h1 style='margin-bottom: -20px;'>Communication Translator</h1>", unsafe_allow_html=True)
    with col_nav:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="back_translator"):
            navigate_to("Home")
        
    st.divider()

    prompt_path = Path("tools/translator/default_prompt.txt")
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = "You are an expert workplace communication assistant. Rewrite the following message to be professional and polite."

    with st.expander("Tool Settings", expanded=False):
        st.markdown("**Model Configuration**")
        if "translator_model" not in st.session_state:
            st.session_state.translator_model = "qwen2.5:7b" 
        
        st.session_state.translator_model = st.text_input("Model", value=st.session_state.translator_model)

    st.markdown("Transform your raw thoughts into professional workplace communication.")
    
    col1, col2 = st.columns(2)
    with col1:
        scenario = st.selectbox(
            "Scenario",
            ["Teams Message", "Email", "Meeting Response", "Status Update", "Escalation", "Vendor Communication", "Manager Communication"]
        )
    with col2:
        tone = st.selectbox(
            "Tone",
            ["Professional", "Friendly", "Manager", "Executive", "Diplomatic", "Direct"]
        )

    raw_message = st.text_area(
        "Input: Raw thought", 
        height=120, 
        placeholder="e.g., Can we confirm if this requirement is final-final or just final_v2?",
        key=f"translator_input_{st.session_state.translator_text_key}"
    )

    col_trans, col_clear, col_empty = st.columns([2, 2, 6])
    
    with col_trans:
        translate_clicked = st.button("Translate", type="primary", use_container_width=True)
        
    with col_clear:
        if st.button("Clear Input", use_container_width=True):
            st.session_state.translator_text_key += 1
            if "translation_result" in st.session_state:
                del st.session_state["translation_result"]
            st.rerun()

    if translate_clicked:
        if not raw_message.strip():
            st.warning("Please enter a message to translate.")
        else:
            with st.spinner(f"Rewriting using {st.session_state.translator_model}..."):
                try:
                    start_total = time.perf_counter()
                    start_ai = time.perf_counter()
                    result_dict = translate_message(
                        st.session_state.translator_model, 
                        system_prompt, 
                        scenario, 
                        tone, 
                        raw_message
                    )
                    ai_duration = int((time.perf_counter() - start_ai) * 1000)
                   
                    st.session_state.translation_result = result_dict.get("rewritten_message", "")
                    st.session_state.detected_emotion = result_dict.get("detected_emotion", "Neutral")
                    
                    total_duration = int((time.perf_counter() - start_total) * 1000)
                    log_usage(
                        "Translator", 
                        "Translate", 
                        total_duration_ms=total_duration,
                        ai_duration_ms=ai_duration,
                        model_name=st.session_state.translator_model,
                        input_size=len(raw_message),
                        output_size=len(st.session_state.translation_result),
                        metadata=f"Tone: {tone}"
                    )
                except Exception as e:
                    st.error(f"Translation failed: {str(e)}")

    if "translation_result" in st.session_state:
        st.subheader("Output: Rewritten Message")
        
        emotion = st.session_state.get("detected_emotion", "Neutral")
        
        if emotion.lower() not in ["neutral", "calm", "polite", "professional", "unknown"]:
            st.warning(f"**Detected Tone:** ⚠ {emotion.title()}")
        else:
            st.info(f"**Detected Tone:** ℹ️ {emotion.title()}")

        st.markdown("*(You can edit the text below before copying it)*")
        st.text_area(
            "Result", 
            st.session_state.translation_result, 
            height=200, 
            label_visibility="collapsed"
        )