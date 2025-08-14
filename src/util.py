import os
import json
from datetime import datetime
import sys

def create_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def create_file(path: str) -> None:
    parent_directory = os.path.dirname(os.path.abspath(path))
    create_directory(parent_directory)
    if not os.path.exists(path):
        with open(path, "w") as _file:
            pass

def save_processing_state(state_path: str, keyword: str, page_number: int) -> None:
    state = {
        "keyword": keyword,
        "last_page": page_number,
        "updated_at": datetime.now().strftime("%H:%M:%S on %B %d, %Y"),
    }
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

def print_err(str):
    print(str, file=sys.stderr)
