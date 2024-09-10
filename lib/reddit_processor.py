import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import pathlib
import hashlib
import requests
import shutil

from urllib.parse import urlparse
from lib.processed_status import ProcessedStatus
from lib.redgif import RedGifs


import praw
import os
import dotenv

def md5hash(filename):
    h  = hashlib.md5()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    rval = h.hexdigest()
    file_size = os.stat(filename).st_size
    return rval + f":{file_size}"

class RedditProcessor:
    def __init__(self, output_dir):
        dotenv.load_dotenv()
        log.info("Reading environment file")

        self.agent_name = os.getenv('agent_name')
        self.client_id = os.getenv("client_id", None)
        self.client_secret = os.getenv("client_secret", None)
        self.client_username = os.getenv("client_username", None)
        self.client_password = os.getenv("client_password", None)
        self.output_dir= output_dir
        self.processed_status = ProcessedStatus(self.output_dir)
        self.images_dir = os.path.join(self.output_dir, "images")
        self.duplicate_dir = os.path.join(self.output_dir, "duplicates")
        self.reddit = None
        self.redgifs = RedGifs()

        assert self.client_id is not None
        assert self.client_secret is not None
        assert self.client_username is not None
        assert self.client_password is not None
        assert self.agent_name is not None

        self.user_agent=f"{self.agent_name} /u/{self.client_username}"

        # Create directory if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        if not os.path.exists(self.duplicate_dir):
            os.makedirs(self.duplicate_dir)

    def login(self):
        self.reddit = praw.Reddit(
            user_agent=self.user_agent,
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.client_username,
            password=self.client_password,
            requestor_kwargs={'timeout': 30}
        )

        # print(self.reddit.user.me())

    def is_image(self, post):
        return post.url.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp'))

    def _get_subreddit_images(self, subreddit_name, listing_type='top', time_filter='all'):
        """
        Generator function to get image posts from a subreddit, filtered by

        :param subreddit_name: Name of the subreddit
        :param listing_type: Type of listing to fetch (e.g., 'hot', 'new', 'top')
        :param time_filter: Time filter for posts (e.g., 'day', 'week', 'month')
        :yield: posts with images
        """
        log.info(f"Checking subreddit {subreddit_name}")
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_method = {'hot': subreddit.hot, 'new': subreddit.new, 'top': subreddit.top,
                        'rising': subreddit.rising, 'controversial': subreddit.controversial}

        if listing_type in ['top', 'controversial']:
            posts = posts_method[listing_type](time_filter=time_filter, limit=None)
        else:
            posts = posts_method[listing_type](limit=None)

        for post in posts:
            # log.info(f"post: {post}")
            if self.processed_status.have_not_seen(post) and self.is_image(post):
                yield post

    def _get_user_images(self, username, listing_type='new', time_filter='all'):
        """
        Generator function to get image posts from a subreddit.

        :param username: Name of the subreddit
        :param listing_type: Type of listing to fetch (e.g., 'hot', 'new', 'top')
        :param time_filter: Time filter for posts (e.g., 'day', 'week', 'month')
        :yield: posts with images
        """
        redditor = self.reddit.redditor(username)
        posts_method = {'hot': redditor.hot, 'new': redditor.new, 'top': redditor.top,
                        'controversial': redditor.controversial}

        if listing_type in ['top', 'controversial']:
            posts = posts_method[listing_type](time_filter=time_filter, limit=None)
        else:
            posts = posts_method[listing_type](limit=None)

        for post in posts:
            if self.processed_status.have_not_seen(post) and hasattr(post, 'url') and self.is_image(post):
                yield post

    def sanitize_filename(self, filename):
        """
        Sanitizes the filename by removing or replacing characters that are invalid for file names.

        :param filename: Original filename
        :return: Sanitized filename
        """
        invalid_chars = '<>:"/\\|?*'

        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def get_filename(self,url):
        fragment_removed = url.split("#")[0]  # keep to left of first #
        query_string_removed = fragment_removed.split("?")[0]
        scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
        if scheme_removed.find("/") == -1:
            return ""
        return os.path.basename(scheme_removed)

    def get_actual_url(self, post):
        url = post.url

        if "i.redgifs.com" in url:
            url = self.redgifs.get_actual_file(url)

        return url

    def download_file(self, post):
        image_url = self.get_actual_url(post)

        try:
            log.info(f"Downloading url: {image_url}")
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
                # ext = response.headers['Content-Type'].split('/')[1]
                filename = os.path.basename(urlparse(image_url).path)
                file_path = os.path.join(self.images_dir, filename)

                # Check if file exists before writing
                if pathlib.Path(file_path).is_file():
                    log.debug(f"File {filename} already downloaded")
                else:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    md5_hash = md5hash(file_path)

                    if md5_hash in self.processed_status.hashes:
                        status = ProcessedStatus.DUPLICATE
                        dup_name = os.path.join(self.duplicate_dir, filename)
                        shutil.move(file_path, dup_name)
                        log.info(f"Duplicate file {filename} moved to duplicates directory")
                    else:
                        status = ProcessedStatus.DOWNLOADED
                        log.info(f"Downloaded {filename}")

                    self.processed_status.hashes.add(md5_hash)
                    self.processed_status.set_status(post.id, status, filename, md5_hash)
            else:
                print(f"Failed to download {image_url}: Non-image or bad status code {response.status_code}")
                self.processed_status.set_status(post.id, ProcessedStatus.ERRORED)

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e}")
            self.processed_status.set_status(post.id, ProcessedStatus.ERRORED)

    def download_user_files(self, username):
        self.login()
        log.info(f"Downloading from user: {username} to {self.output_dir}")
        cnt_downloaded = 0
        for post in self._get_user_images(username):
           self.download_file(post)
           cnt_downloaded += 1

        self.processed_status.save_processed_file()
    def download_subreddit(self, subreddit):
        self.login()
        log.info(f"Downloading from subreddir: {subreddit} to {self.output_dir}")
        cnt_downloaded = 0
        for post in self._get_subreddit_images(subreddit, 'new'):
            self.download_file(post)
            cnt_downloaded += 1

        self.processed_status.save_processed_file()

