import os
import requests
import json
import logging
import time
import asyncio
import aiohttp
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

DISCOURSE_URL = os.getenv("DISCOURSE_URL")
API_KEY = os.getenv("API_KEY")
API_USERNAME = os.getenv("API_USERNAME")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("discourse_topics.log"), logging.StreamHandler()]
)

# Headers for API requests
HEADERS = {
    "Api-Key": API_KEY,
    "Api-Username": API_USERNAME,
    "Content-Type": "application/json"
}

# Configurable settings
RETRY_LIMIT = 3  # Max retries for failed API calls
RATE_LIMIT_DELAY = 1  # Delay between API calls (in seconds)
TIMEOUT = 10  # Timeout for HTTP requests (seconds)

async def create_topic(session, title, body, category=None, image_url=None, image_position="end", formatting=None, embed_url=None, external_id=None, user_api_key=None, user_api_username=None):
    """
    Creates a new topic asynchronously from a custom user account.

    Args:
        title (str): The title of the topic.
        body (str): The body/content of the topic.
        category (int): The category for the topic (optional).
        image_url (str): The URL of an image to include (optional).
        image_position (str): Position of the image in the body ('start', 'end', 'inline').
        formatting (dict): Markdown formatting options (bold, italic, headers).
        embed_url (str): External URL to embed.
        external_id (str): External ID to associate with the topic.
        user_api_key (str): API key of the user posting the topic.
        user_api_username (str): Username of the user posting the topic.

    Returns:
        dict: Response JSON from the Discourse API, or None if failed.
    """
    url = f"{DISCOURSE_URL}/posts.json"
    data = {
        "title": title,
        "raw": body,
        "category": category,
        "embed_url": embed_url,
        "external_id": external_id
    }

    # Remove None values from the data dictionary
    data = {k: v for k, v in data.items() if v is not None}

    # Apply Markdown formatting
    if formatting:
        if formatting.get("bold"):
            body = f"**{body}**"
        if formatting.get("italic"):
            body = f"*{body}*"
        if formatting.get("header"):
            body = f"# {body}"

    # Insert image at the specified position
    if image_url:
        image_markdown = f"![Image]({image_url})"
        if image_position == "start":
            body = f"{image_markdown}\n\n{body}"
        elif image_position == "end":
            body = f"{body}\n\n{image_markdown}"
        elif image_position == "inline":
            body = body.replace("[IMAGE]", image_markdown)

    # Finalize body with formatted text
    data["raw"] = body

    # Set custom user API headers if provided
    headers = {
        "Api-Key": user_api_key or API_KEY,  # Use provided API key or default
        "Api-Username": user_api_username or API_USERNAME,  # Use provided username or default
        "Content-Type": "application/json"
    }

    try:
        async with session.post(url, headers=headers, json=data, timeout=TIMEOUT) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as err:
        logging.error(f"Error creating topic '{title}': {err}")
        return None


async def add_multiple_topics(topics, users_info=None):
    """
    Create multiple topics asynchronously with progress tracking and detailed logging from custom accounts.

    Args:
        topics (list): List of dictionaries with topic details.
        users_info (list): List of dictionaries with user API keys and usernames (optional).
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, topic in enumerate(tqdm(topics, desc="Creating Topics", unit="topic")):
            title = topic.get("title")
            body = topic.get("body", "")
            category = topic.get("category")
            image_url = topic.get("image_url")
            image_position = topic.get("image_position", "end")
            formatting = topic.get("formatting", {})
            embed_url = topic.get("embed_url")
            external_id = topic.get("external_id")

            # Determine which account to use (either from default or custom list)
            if users_info:
                user_info = users_info[i % len(users_info)]  # Loop through users if there are more topics than users
                user_api_key = user_info["api_key"]
                user_api_username = user_info["username"]
            else:
                user_api_key = None
                user_api_username = None

            task = create_topic(session, title, body, category, image_url, image_position, formatting, embed_url, external_id, user_api_key, user_api_username)
            tasks.append(task)

        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)

        # Log results
        for response, topic in zip(responses, topics):
            title = topic.get("title")
            if response:
                logging.info(f"Created topic '{title}' with ID {response['post_number']}")
            else:
                logging.error(f"Failed to create topic '{title}'")


def load_topics_from_json(file_path):
    """
    Load topics from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: A list of topic dictionaries.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            topics = json.load(file)
            return topics
    except Exception as e:
        logging.error(f"Failed to load topics from file: {e}")
        return []


if __name__ == "__main__":
    # Load topics from an external JSON file
    topics_file = "topics.json"
    topics = load_topics_from_json(topics_file)

    users_info = [
    {"api_key": os.getenv("USER1_API_KEY"), "username": os.getenv("USER1_USERNAME")},  
    {"api_key": os.getenv("USER2_API_KEY"), "username": os.getenv("USER2_USERNAME")},  
    {"api_key": os.getenv("USER3_API_KEY"), "username": os.getenv("USER3_USERNAME")},  
    {"api_key": os.getenv("USER4_API_KEY"), "username": os.getenv("USER4_USERNAME")},  
    {"api_key": os.getenv("USER5_API_KEY"), "username": os.getenv("USER5_USERNAME")},  
    {"api_key": os.getenv("USER6_API_KEY"), "username": os.getenv("USER6_USERNAME")},  
    {"api_key": os.getenv("USER7_API_KEY"), "username": os.getenv("USER7_USERNAME")},  
    {"api_key": os.getenv("USER8_API_KEY"), "username": os.getenv("USER8_USERNAME")},  
    {"api_key": os.getenv("USER9_API_KEY"), "username": os.getenv("USER9_USERNAME")},

]

    if topics:
        # Run the async function to create topics
        asyncio.run(add_multiple_topics(topics, users_info))
    else:
        logging.error("No topics to process. Please check the JSON file.")
