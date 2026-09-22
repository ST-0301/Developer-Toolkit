import webview
import threading
import subprocess
import time
import sys
import urllib.request

def start_streamlit():
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def inject_zoom_script(window):
    zoom_js = """
    (function() {
        if (window._zoomInitialized) return;
        window._zoomInitialized = true;
        
        // Ensure minimum height fills viewport layout on zoom out
        const style = document.createElement('style');
        style.innerHTML = `
            html, body, [data-testid="stAppViewContainer"], .stApp {
                min-height: 100vh !important;
                height: 100% !important;
                margin: 0 !important;
            }
        `;
        document.head.appendChild(style);
        
        let zoomLevel = 1.0;
        window.addEventListener('wheel', function(e) {
            if (e.ctrlKey) {
                e.preventDefault();
                if (e.deltaY < 0) {
                    zoomLevel = Math.min(zoomLevel + 0.1, 3.0);
                } else {
                    zoomLevel = Math.max(zoomLevel - 0.1, 0.3);
                }
                document.body.style.zoom = zoomLevel;
            }
        }, { passive: false });
    })();
    """
    window.evaluate_js(zoom_js)

if __name__ == '__main__':
    t = threading.Thread(target=start_streamlit)
    t.daemon = True
    t.start()
    
    time.sleep(2)
    
    window = webview.create_window(
        title="Developer Toolkit", 
        url="http://localhost:8501",
        width=1200, 
        height=800,
        text_select=True
    )
    
    def on_loaded(*args):
        inject_zoom_script(window)

    window.events.loaded += on_loaded
    
    webview.start()