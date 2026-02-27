import os

UPLOAD_ROOT = "uploads"

def save_document(file, terminal):
    terminal_path = os.path.join(UPLOAD_ROOT, terminal)

    # Create terminal folder if not exists
    os.makedirs(terminal_path, exist_ok=True)

    file_path = os.path.join(terminal_path, file.name)

    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    return file_path


def get_terminal_folders():
    if not os.path.exists(UPLOAD_ROOT):
        return []

    return [f for f in os.listdir(UPLOAD_ROOT)
            if os.path.isdir(os.path.join(UPLOAD_ROOT, f))]


def get_files_in_terminal(terminal):
    terminal_path = os.path.join(UPLOAD_ROOT, terminal)

    if not os.path.exists(terminal_path):
        return []

    return os.listdir(terminal_path)
