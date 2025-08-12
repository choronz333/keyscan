import os
import json
from datetime import datetime
import sys

def create_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)

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
