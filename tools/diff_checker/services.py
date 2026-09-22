import difflib
import json

def preprocess_text(text, ignore_blank_lines=False, ignore_case=False):
    """Applies user filters before comparison."""
    lines = text.splitlines()
    
    if ignore_blank_lines:
        lines = [line for line in lines if line.strip() != ""]
        
    if ignore_case:
        lines = [line.lower() for line in lines]
        
    return '\n'.join(lines)

def get_diff_stats(original_text, updated_text):
    """Calculates lines added, removed, and overall similarity."""
    orig_lines = original_text.splitlines()
    upd_lines = updated_text.splitlines()
    
    matcher = difflib.SequenceMatcher(None, orig_lines, upd_lines)
    similarity = round(matcher.ratio() * 100, 1)
    
    added = 0
    removed = 0
    modified = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'insert':
            added += (j2 - j1)
        elif tag == 'delete':
            removed += (i2 - i1)
        elif tag == 'replace':
            modified_count = max((i2 - i1), (j2 - j1))
            modified += modified_count

    return added, removed, modified, similarity

def generate_monaco_diff_html(original_text, updated_text, language="javascript", theme="vs"):
    """
    Embeds the VS Code Monaco Editor directly into the Streamlit app.
    Theme options: 'vs' (light), 'vs-dark' (dark), 'hc-black' (high contrast).
    """
    safe_original = json.dumps(original_text).replace("<", "\\u003c").replace(">", "\\u003e")
    safe_updated = json.dumps(updated_text).replace("<", "\\u003c").replace(">", "\\u003e")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }}
            #container {{ width: 100%; height: 100vh; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs/loader.min.js"></script>
    </head>
    <body>
        <div id="container"></div>
        <script>
            require.config({{ paths: {{ 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' }} }});
            require(['vs/editor/editor.main'], function() {{
                
                // Initialize the Diff Editor
                var diffEditor = monaco.editor.createDiffEditor(document.getElementById('container'), {{
                    enableSplitViewResizing: false,
                    renderSideBySide: true,
                    theme: '{theme}',
                    readOnly: true,
                    automaticLayout: true,
                    scrollBeyondLastLine: false,
                    ignoreTrimWhitespace: false
                }});

                // Inject the text data
                diffEditor.setModel({{
                    original: monaco.editor.createModel({safe_original}, '{language}'),
                    modified: monaco.editor.createModel({safe_updated}, '{language}')
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_content