import os

from args import parse_args
from util import create_directory, print_err, save_processing_state
from search import search_gists


def main() -> int:
    args = parse_args()

    create_directory(os.path.dirname(args.output_path))

    processed_pages = 0
    current_page_number = args.start_page

    try:
        for page_number, gist_ids in search_gists(
            args.keyword, start_page=current_page_number, delay_seconds=args.delay
        ):
            processed_pages += 1
            current_page_number = page_number
            print(f"Page {page_number}:")
            print(f"Gists found: {gist_ids}")

            if args.max_pages != None and processed_pages >= args.max_pages:
                print("Reached page limit. Exiting...")
                break
            save_processing_state(args.output_path, args.keyword, current_page_number)

    except KeyboardInterrupt:
        print(f"Interrupted at page {current_page_number}.")
        print(f"Successfully processed {processed_pages - 1} pages.")
        return 130

    except Exception as exception:
        print_err(f"Error on page {current_page_number}: {exception}")
        return 1

    finally:
        save_processing_state(args.output_path, args.keyword, current_page_number)

    # Finished searching
    if processed_pages == 0:
        print(f'No results found for keyword "{args.keyword}".')
    else:
        print("Search finished.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
