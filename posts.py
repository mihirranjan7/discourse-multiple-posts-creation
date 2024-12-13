import os
import requests
import json
import logging
import time
import asyncio
import aiohttp
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

DISCOURSE_URL = os.getenv("DISCOURSE_URL")
API_KEY = os.getenv("API_KEY")
API_USERNAME = os.getenv("API_USERNAME")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("discourse_topics.log"), logging.StreamHandler()]
)

HEADERS = {
    "Api-Key": API_KEY,
    "Api-Username": API_USERNAME,
    "Content-Type": "application/json"
}

RETRY_LIMIT = 3
RATE_LIMIT_DELAY = 1
TIMEOUT = 10

async def create_topic(session, title, body, category=None, image_url=None, image_position="end", formatting=None, embed_url=None, external_id=None, user_api_key=None, user_api_username=None):
    url = f"{DISCOURSE_URL}/posts.json"
    data = {
        "title": title,
        "raw": body,
        "category": category,
        "embed_url": embed_url,
        "external_id": external_id
    }
    data = {k: v for k, v in data.items() if v is not None}

    if formatting:
        if formatting.get("bold"):
            body = f"**{body}**"
        if formatting.get("italic"):
            body = f"*{body}*"
        if formatting.get("header"):
            body = f"# {body}"

    if image_url:
        image_markdown = f"![Image]({image_url})"
        if image_position == "start":
            body = f"{image_markdown}\n\n{body}"
        elif image_position == "end":
            body = f"{body}\n\n{image_markdown}"
        elif image_position == "inline":
            body = body.replace("[IMAGE]", image_markdown)

    data["raw"] = body

    headers = {
        "Api-Key": user_api_key or API_KEY,
        "Api-Username": user_api_username or API_USERNAME,
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

            if users_info:
                user_info = users_info[i % len(users_info)]
                user_api_key = user_info["api_key"]
                user_api_username = user_info["username"]
            else:
                user_api_key = None
                user_api_username = None

            task = create_topic(session, title, body, category, image_url, image_position, formatting, embed_url, external_id, user_api_key, user_api_username)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response, topic in zip(responses, topics):
            title = topic.get("title")
            if response:
                logging.info(f"Created topic '{title}' with ID {response['post_number']}")
            else:
                logging.error(f"Failed to create topic '{title}'")


def load_topics_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            topics = json.load(file)
            return topics
    except Exception as e:
        logging.error(f"Failed to load topics from file: {e}")
        return []


if __name__ == "__main__":
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
        asyncio.run(add_multiple_topics(topics, users_info))
    else:
        logging.error("No topics to process. Please check the JSON file.")
