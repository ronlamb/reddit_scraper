import os
import pickle

"""
class ProcessedStatus

Handles the processed status of the current user or subreddit.

Information is stored in a dictionary that is saved in a pickle file.

The dictionary is setup as follows
    key: The post.id
    value: a tuple containing ( status, filename, hash) 

    Status is one of:
        0 - DOWNLOADED
        1 - ERRORED
        3 - SKIPPED
"""
class ProcessedStatus:
    DOWNLOADED = 0
    ERRORED = 1
    SKIPPED = 2

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.processed_file = os.path.join(self.output_dir, "processed.pkl")
        self.processed = self.load_processed_file()
        self.hashes = set()

        for key, value in self.processed.items():
            self.hashes.add(value[2])

    def load_processed_file(self):
        if not os.path.exists(self.processed_file):
            return {}

        with open(self.processed_file, 'rb') as f:
            return pickle.load(f)

    def save_processed_file(self):
        with open(self.processed_file, 'wb') as f:
            pickle.dump(self.processed, f)

    def have_not_seen(self, post):
        return post.id not in self.processed
        # return post.id not in self.processed_posts and post.id not in self.errored_posts

    def set_status(self, id, status, filename=None, hash=None):
        self.processed[id] = ( status, filename, hash )
