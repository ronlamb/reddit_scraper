import logging
from urllib.parse import urlparse

import requests

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

import praw
import os

import dotenv
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
        self.processed_files = os.path.join(self.output_dir, "processed.txt")
        self.processed_posts = self._load_processed_posts()
        self.images_dir = os.path.join(self.output_dir, "images")
        self.reddit = None

        assert self.client_id is not None
        assert self.client_secret is not None
        assert self.client_username is not None
        assert self.client_password is not None
        assert self.agent_name is not None

        self.user_agent=f"{self.agent_name} /u/{self.client_username}"

        # Create directory if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

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

    def _load_processed_posts(self):
        """
        Loads IDs of previously processed posts from a file.

        :param filename: File containing the IDs
        :return: Set of post IDs
        """
        if not os.path.exists(self.processed_files):
            return set()
        with open(self.processed_files, 'r') as file:
            return set(file.read().splitlines())

    def _get_subreddit_images(self, subreddit_name, listing_type='top', time_filter='all'):
        """
        Generator function to get image posts from a subreddit.

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
            log.info(f"post: {post}")
            if post.id not in self.processed_posts and post.url.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp')):
                yield post

    def _get_user_images(self, username, listing_type='new', time_filter='all'):
        """
        Generator function to get image posts from a subreddit.

        :param username: Name of the subreddit
        :param processed_list: Set of post IDs that have been processed
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
            if post.id not in self.processed_posts and hasattr(post, 'url') and post.url.endswith(('jpg', 'jpeg', 'png', 'gif', 'webp')):
                yield post

    def sanitize_filename(self,filename):
        """
        Sanitizes the filename by removing or replacing characters that are invalid for file names.

        :param filename: Original filename
        :return: Sanitized filename
        """
        invalid_chars = '<>:"/\\|?*'

        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def add_to_processed_file(self, id):
        with open(self.processed_files, 'a') as fp:
            fp.write(f'{id}\n')
        self.processed_posts.add(id)

    def download_file(self, post):
        image_url = post.url
        # image_filename = self.sanitize_filename(image_url.split("/")[-1])
        # image_path = os.path.join(self.images_dir, image_filename)

        try:
            log.info(f"Downloading url: {image_url}")
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
                # ext = response.headers['Content-Type'].split('/')[1]
                filename = os.path.basename(urlparse(image_url).path)
                file_path = os.path.join(self.images_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {file_path}")
                self.add_to_processed_file(post.id)
            else:
                print(f"Failed to download {image_url}: Non-image or bad status code {response.status_code}")
                self.add_to_processed_file(post.id)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e}")

    def download_user_files(self, username):
        self.login()
        log.info(f"Downloading from user: {username} to {self.output_dir}")
        cnt_downloaded = 0
        for post in self._get_user_images(username):
           self.download_file(post)
           cnt_downloaded += 1


    def download_subreddit(self, subreddit):
        self.login()
        log.info(f"Downloading from subreddir: {subreddit} to {self.output_dir}")
        cnt_downloaded = 0
        for post in self._get_subreddit_images(subreddit, 'new'):
            self.download_file(post)
            cnt_downloaded += 1

