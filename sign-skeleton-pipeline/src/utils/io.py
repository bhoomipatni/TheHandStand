import os
import json

def load_json(file_path):
    """Load a JSON file from the specified path."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save data to a JSON file at the specified path."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def ensure_directory_exists(directory):
    """Ensure that a directory exists; if not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def list_files_in_directory(directory):
    """List all files in the specified directory."""
    return os.listdir(directory) if os.path.exists(directory) else []