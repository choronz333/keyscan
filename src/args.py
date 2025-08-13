import os
import argparse
import time
from dataclasses import dataclass


@dataclass
class Arguments:
    keyword: str
    model: str
    start_page: int
    max_pages: int | None
    file_type: str
    output_path: str
    delay: float


def parse_args() -> Arguments:
    parser = argparse.ArgumentParser(
        prog="Keyscan", description="Keyscan: GitHub Gists scanner."
    )
    parser.add_argument(
        "--keyword",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
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
        default=2,
        help="Optional delay between requests in seconds",
    )
    return Arguments(**vars(parser.parse_args()))
