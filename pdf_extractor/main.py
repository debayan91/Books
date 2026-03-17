import os
import sys
import threading
import time
import webbrowser
from server import app

def start_server():
    # Run the Flask app on localhost:5000, disabling the reloader
    # so it doesn't spawn extra threads/processes.
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def main():
    print("Starting PDF Merge Tool server...")
    # Start the server in a daemon thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait briefly for server to boot up
    time.sleep(1.5)
    
    url = "http://127.0.0.1:5000"
    print(f"Opening browser at {url} ...")
    webbrowser.open(url)
    
    # Keep the main process alive
    print("Press Ctrl+C to stop the application.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()
