import os
import subprocess
import time
import webbrowser
import sys

def run_app():
    # Set the working directory to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    print("Starting Quiet Alert server...")
    
    # Start the Flask server as a subprocess
    # We use sys.executable to ensure we use the same Python interpreter
    server_process = subprocess.Popen(
        [sys.executable, "web_app/web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    if server_process.stdout is None:
        print("Error: Could not capture server output.")
        server_process.terminate()
        return

    # Wait for the server to start (check for output or just wait)
    # The server usually starts within 2-3 seconds
    print("Waiting for server to initialize...")
    time.sleep(3)

    # Open the browser
    url = "http://localhost:8080"
    print(f"Opening browser at {url}...")
    webbrowser.open(url)

    print("\nQuiet Alert is running!")
    print("Press Ctrl+C to stop the server.")

    try:
        # Keep the script running and stream server output
        while True:
            line = server_process.stdout.readline()
            if line:
                print(f"[Server] {line.strip()}")
            if server_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    run_app()
