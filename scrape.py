#  Main image scraper process
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import os

from lib.reddit_processor import RedditProcessor


def get_arguments():
    parser = argparse.ArgumentParser()

    # Allow only sunreddit or username to be pulled
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--subreddit", help="Subreddit name", type=str)
    group.add_argument("-u","--username", help="Subreddit user", type=str)

    parser.add_argument("-o", "--output_dir", help="Output dir", action='store',  type=str, default="output")

    rval = parser.parse_args()

    if rval.username:
        rval.output_dir = os.path.join(rval.output_dir,"user", rval.username)
    else:
        rval.output_dir = os.path.join(rval.output_dir, "subreddit", rval.subreddit)

    return rval

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = get_arguments()
    processor = RedditProcessor(args.output_dir)

    if args.username:
        processor.download_user_files(args.username)
    else:
        processor.download_subreddit(args.subreddit)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
