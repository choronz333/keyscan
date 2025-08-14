import os
import traceback

from args import parse_args
from util import create_directory, print_err, save_processing_state
from search import search_gists
from process import process_gist
from scanned_db import ScannedDb


def main() -> int:
    args = parse_args()

    create_directory(os.path.dirname(args.output_path))

    database = ScannedDb(args.scanned_db)

    processed_pages = 0
    processed_gists = 0
    current_page_number = args.start_page

    try:
        for page_number, gist_ids in search_gists(
            args.keyword,
            start_page=current_page_number,
            file_type=args.file_type,
            delay_seconds=args.delay,
        ):
            processed_pages += 1
            current_page_number = page_number
            print(f"Page {page_number}:")
            print(f"Gists found: {gist_ids}")

            output_dir = os.path.dirname(args.output_path)
            for gist_id in gist_ids:
                if database.seen(gist_id):
                    print(f"Skipping already scanned gist: {gist_id}")
                    continue

                print(f"Processing gist \"{gist_id}\"...")
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

            if args.max_pages != None and processed_pages >= args.max_pages:
                print("Reached page limit. Exiting...")
                break
            save_processing_state(args.output_path, args.keyword, current_page_number)

    except KeyboardInterrupt:
        print(f"Interrupted at page {current_page_number}.")
        print(f"Successfully processed {processed_pages - 1} pages.")
        print(f"Successfully processed {processed_gists} gists.")
        return 130

    except Exception as exception:
        print_err(f"Error on page {current_page_number}: {exception}")
        print_err(''.join(traceback.TracebackException.from_exception(exception).format()))
        print(f"Successfully processed {processed_gists} gists.")
        return 1

    finally:
        save_processing_state(args.output_path, args.keyword, current_page_number)

    # Finished searching
    if processed_pages == 0:
        print(f'No results found for keyword "{args.keyword}".')
    else:
        print(f"Successfully processed {processed_pages} pages.")
        print(f"Successfully processed {processed_gists} gists.")
        print("Search finished.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
