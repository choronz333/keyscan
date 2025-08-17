from typing import Set

from src.util import create_file, print_err


class ScannedDb:
    """
    File backed database of scanned gist IDs. Stores one gist per line.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        create_file(file_path)
        self.scanned: Set[str] = set()
        self.load()

    def load(self) -> None:
        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    gist_id = line.strip()
                    if gist_id != "":
                        self.scanned.add(gist_id)
        except FileNotFoundError:
            print_err("Database file not found.")
            pass

    def seen(self, gist_id: str) -> bool:
        return gist_id in self.scanned

    def add(self, gist_id: str) -> None:
        if gist_id in self.scanned:
            return
        self.scanned.add(gist_id)
        with open(self.file_path, "a") as file:
            file.write(gist_id + "\n")
