import webbrowser
import threading
import time
from app import app

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 FinTrack: Personal Finance & Attendance Tracker")
    print("  🌐 Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    
    # Automatically open default web browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask server
    app.run(host="127.0.0.1", port=5000, debug=False)
