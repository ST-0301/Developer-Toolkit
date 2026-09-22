import webview
import threading
import subprocess
import time
import sys
import os

def start_streamlit():
    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == '__main__':
    t = threading.Thread(target=start_streamlit)
    t.daemon = True
    t.start()
    
    time.sleep(2)
    
    webview.create_window(
        title="Developer Toolkit", 
        url="http://localhost:8501",
        width=1200, 
        height=800,
        text_select=True
    )
    
    webview.start()