from typing import List


def filter_lines(text: str, file_type: str) -> List[str]:
    """
    Split into lines, strip whitespace, remove # and // comments, drop empty lines.

    TODO: Normalize based on file_type (Possible?)
    """
    candidate_lines: List[str] = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or line.startswith("//") or len(line) <= 0:
            continue
        candidate_lines.append(line)

    return candidate_lines


def normalize_all_contents(contents: List[str], file_type: str) -> List[str]:
    """Normalize multiple file contents and return a single list of lines."""
    all_lines: List[str] = []
    for content in contents:
        all_lines.extend(filter_lines(content, file_type))
    return all_lines
