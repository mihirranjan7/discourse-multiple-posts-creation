# Discourse Multiple Posts Creation

The **posts** Python script allows you to asynchronously create multiple topics on a Discourse forum using different user accounts and API keys. It creates posts in a revolving manner, moving through each user account one by one. Once all users have been used, it loops back to the first user and continues posting.

## Features

- Create multiple topics asynchronously, using a revolving set of user API keys
- Configurable options for each post (e.g., title, body, category, image, formatting)
- Looping through user accounts to distribute posts evenly
- Error logging and progress tracking

## Requirements

- Python 3.7+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mihirranjan7/discourse-multiple-posts-creation.git
cd discourse-multiple-posts-creation
```

### 2. Set up environment variables

Create a `.env` file to store your Discourse API credentials and user details. You’ll need to define:

- `DISCOURSE_URL`: Your Discourse forum URL
- `API_KEY`: Your Discourse API key
- `API_USERNAME`: Your Discourse API username
- `USERn_API_KEY`: API key for each user account
- `USERn_USERNAME`: Username for each user account

### 3. Prepare topics JSON file

Create a `topics.json` file with the details of each post to be created. This file will contain a list of topic objects, and each object will have properties like the title, body, category, etc.

### 4. Run the script

Run the script to start creating posts. The script will use each user’s API key and username in a revolving manner until all topics are created:

```bash
python posts.py
```

Once all users have been used, the script will loop back to the first user and continue posting.

Logs will be saved to `discourse_topics.log`.

## License

MIT License

---
