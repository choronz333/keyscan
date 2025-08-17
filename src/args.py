import os
import argparse
import time
from dataclasses import dataclass


@dataclass
class Arguments:
    keywords_file: str
    model: str
    file_type: str
    output_path: str
    delay: float
    scanned_db: str


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(
        prog="Keyscan", description="Keyscan: GitHub Gists scanner."
    )
    parser.add_argument(
        "--keywords-file",
        type=str,
        required=True,
        help="Path to a newline-separated list of keywords to search",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--file-type",
        type=str,
        default="Dotenv",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default=os.path.join("output", f"state_{round(time.time())}.json"),
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5,
        help="Optional delay between requests in seconds",
    )
    parser.add_argument(
        "--scanned-db",
        type=str,
        default=os.path.join("output", "scanned.txt"),
        help="Path to a newline-separated file of scanned gist IDs",
    )
    return Arguments(**vars(parser.parse_args()))
