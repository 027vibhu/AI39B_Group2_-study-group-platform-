import os
import socket
import sys
import subprocess

# If the user runs this with the system Python, redirect to the project virtualenv Python.
venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
if not sys.executable.lower().startswith(os.path.join(os.getcwd(), '.venv').lower()) and os.path.exists(venv_python):
    print(f"Switching to virtualenv Python at {venv_python}")
    return_code = subprocess.call([venv_python] + sys.argv)
    sys.exit(return_code)

from app import create_app, socketio

app = create_app()


def find_available_port(start_port=5000, max_port=5010):
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise OSError(f"No available ports found between {start_port} and {max_port}.")


if __name__ == "__main__":
    preferred_port = int(os.environ.get('PORT', 5000))
    port = find_available_port(preferred_port)
    if port != preferred_port:
        print(f"Port {preferred_port} is in use. Starting on port {port} instead.")
    socketio.run(app, host='127.0.0.1', port=port, debug=True)