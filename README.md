# Reddit Scraper

This script will download images from reddit posts.  It uses the praw library to access
Reddit's API.

## Requirements
- Python 3.10 or higher

## Building

```code
pip install -r requirements.txt
```

The above command will install the following libraries
- requests
- praw (Python Reddit API Wrapper)
- python-dotenv

## Setup Env file
Create a Reddit app on reddit's [app creation](https://www.reddit.com/prefs/apps) page.

Follow the prompts to create a new app and once it's done you should see a new app like the following.

![Reddit Info](reddit_app_image.png)

Once you get an email back that it's been approved you can then setup your environment.  

### .env file
To simplify this, the python-dotenv library is used.  Create a .env in the root
directory where you cloned the repo.

The following variables are used:

| Variable | Value |
| -------- | ----- |
| agent_name | Name of the app you created.  In the example above it's reddit_scraper. |
| client_id | The client ID.  In the example above it would be the text where the X's are shown. | 
| client_secret | The secret.  Click on edit and copy the value of the secret shown. |
| client_username | Your reddit username |
| client_password | Your reddit password |

example:
```
agent_name=reddit_scraper
client_id=XXXXXXXXXXXXXXXXXXXXXX
client_secret=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
client_username=username
client_password=some_password
```

## Running
