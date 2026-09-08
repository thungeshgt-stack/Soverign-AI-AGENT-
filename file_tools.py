"""
Generic file save/list helpers for uploaded content.
"""
import os


def save_uploaded_file(uploaded_file, target_dir: str) -> str:
    """Save a Streamlit UploadedFile to target_dir, return full path."""
    os.makedirs(target_dir, exist_ok=True)
    path = os.path.join(target_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def list_files(directory: str) -> list:
    if not os.path.isdir(directory):
        return []
    return sorted(os.listdir(directory))
