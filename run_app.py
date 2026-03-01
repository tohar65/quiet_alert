import os
import subprocess
import sys
import argparse
import time
import webbrowser
from typing import List, Optional

def run_command(command: List[str], cwd: Optional[str] = None) -> int:
    """Run a command and return the return code."""
    try:
        process = subprocess.run(command, cwd=cwd, check=False)
        return process.returncode
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return 1

def install_dependencies():
    """Installs all necessary dependencies."""
    print("Installing dependencies...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Install oref_alert_parser in editable mode
    oref_parser_path = os.path.join(project_root, "oref_alert_parser")
    print("Installing oref_alert_parser...")
    if run_command([sys.executable, "-m", "pip", "install", "-e", oref_parser_path], cwd=project_root) != 0:
        print("Failed to install oref_alert_parser.")
        sys.exit(1)

    # Install web_app requirements
    web_app_reqs = os.path.join(project_root, "web_app", "requirements.txt")
    print("Installing web_app requirements...")
    if run_command([sys.executable, "-m", "pip", "install", "-r", web_app_reqs], cwd=project_root) != 0:
        print("Failed to install web_app requirements.")
        sys.exit(1)

    # Install test requirements
    test_reqs = os.path.join(project_root, "requirements-test.txt")
    print("Installing test requirements...")
    if run_command([sys.executable, "-m", "pip", "install", "-r", test_reqs], cwd=project_root) != 0:
        print("Failed to install test requirements.")
        sys.exit(1)

    print("All dependencies installed successfully.")

def serve():
    """Starts the Flask web server."""
    install_dependencies()
    print("Starting Quiet Alert server...")
    
    # Set the working directory to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Start the Flask server as a subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    
    server_process = subprocess.Popen(
        [sys.executable, "web_app/web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=project_root,
        env=env
    )

    if server_process.stdout is None:
        print("Error: Could not capture server output.")
        server_process.terminate()
        return

    # Wait for the server to start
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

def run_tests():
    """Runs the full pytest suite."""
    print("Running full test suite...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    returncode = run_command([sys.executable, "-m", "pytest"], cwd=project_root)
    if returncode == 0:
        print("\nAll tests passed successfully!")
    else:
        print(f"\nTests failed with return code {returncode}")
    sys.exit(returncode)

def update_locations():
    """Updates the approved locations list."""
    print("Updating approved locations list...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure we are in the right path for the imports to work if we were to import it, 
    # but we will run it as a script for simplicity.
    log_file = os.path.join(project_root, "alerts.log")
    if not os.path.exists(log_file):
        print(f"Warning: {log_file} not found. Creating an empty one or please run the app first to generate alerts.")
        # We can't really update if there's no log.
        # But maybe we want to run the parser first?
        # The instruction says "Runs the oref_alert_parser logic to update the approved locations list."
    
    updater_script = os.path.join(project_root, "oref_alert_parser", "oref_alert_parser", "locations_updater.py")
    
    # Run the locations_updater script
    # It expects log_file as an argument
    returncode = run_command([sys.executable, updater_script, log_file], cwd=project_root)
    
    if returncode == 0:
        print("Locations updated successfully.")
    else:
        print(f"Failed to update locations. Return code: {returncode}")
    sys.exit(returncode)

def main():
    parser = argparse.ArgumentParser(description="Quiet Alert Project CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    subparsers.add_parser("serve", help="Installs dependencies and starts the Flask web server (default)")

    # Install command
    subparsers.add_parser("install", help="Installs all necessary dependencies")

    # Test command
    subparsers.add_parser("test", help="Runs the full pytest suite")

    # Update locations command
    subparsers.add_parser("update-locations", help="Updates the approved locations list")

    args = parser.parse_args()

    # Default to serve if no command provided
    if args.command == "serve" or args.command is None:
        serve()
    elif args.command == "install":
        install_dependencies()
    elif args.command == "test":
        run_tests()
    elif args.command == "update-locations":
        update_locations()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
