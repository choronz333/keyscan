import os
import traceback
from typing import List

from args import parse_args
from util import create_directory, print_err, save_processing_state
from search import search_gists
from process import process_gist
from scanned_db import ScannedDb


def get_keywords(keywords_file: str) -> List[str]:
    keywords = []
    try:
        with open(keywords_file, "r") as file:
            for line in file:
                keyword = line.strip()
                if keyword:
                    keywords.append(keyword)
        return keywords
    except FileNotFoundError as exception:
        print_err(f"Keywords file not found: {keywords_file}")
        raise exception


def search_one_keyword(keyword: str, args, database: ScannedDb) -> int:
    """
    Search all gists given a file type matching a keyword.

    Returns the total number of gists processed.
    """
    processed_gists = 0

    for page_number, gist_ids in search_gists(
        keyword,
        file_type=args.file_type,
        delay_seconds=args.delay,
    ):
        print(f"Keyword '{keyword}' — Page {page_number}:")
        print(f"Gists found: {gist_ids}")

        output_dir = os.path.dirname(args.output_path)
        for gist_id in gist_ids:
            if database.seen(gist_id):
                print(f"Skipping already scanned gist: {gist_id}")
                continue

            print(f'Processing gist "{gist_id}"...')
            results = process_gist(
                gist_id=gist_id,
                file_type=args.file_type,
                model=args.model,
                output_dir=output_dir,
            )
            processed_gists += 1
            if len(results) > 0:
                print(f"Processed {gist_id}: {len(results)} record(s) saved.")
                for result in results:
                    print(result)

            database.add(gist_id)

        save_processing_state(args.output_path, keyword, page_number)

    return processed_gists


def main() -> int:
    args = parse_args()

    create_directory(os.path.dirname(args.output_path))

    database = ScannedDb(args.scanned_db)

    total_gists = 0

    try:
        keywords_list = get_keywords(args.keywords_file)
        for keyword in keywords_list:
            gists_processed = search_one_keyword(keyword, args, database)
            total_gists += gists_processed

    except KeyboardInterrupt:
        print("Interrupted.")
        print(f"Successfully processed {total_gists} gists.")
        return 130

    except Exception as exception:
        print_err(f"Error: {exception}")
        print_err(
            "".join(traceback.TracebackException.from_exception(exception).format())
        )
        print(f"Successfully processed {total_gists} gists.")
        return 1

    print(f"Successfully processed {total_gists} gists.")
    print("Search finished.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
