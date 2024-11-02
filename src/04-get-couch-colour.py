"""
This file classifies the color of couches in the images extracted from the Never Too Small videos.

It does this using natural language with the help of the OpenAI API.
"""

import os
import json
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, BadRequestError, OpenAIError

# Define paths
VIDEO_LIST_PATH = "data/couch_info.json"
CLASSIFICATIONS_DIR = "data/couch_colour_classifications_2"
IMAGE_URL_TEMPLATE = "https://github.com/j-jayes/grey-couches/blob/main/data/couch_images/{video_id}_couch.jpg?raw=true"

# Load environment variables from .env file
load_dotenv()

# Initialize API client with the retrieved API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CouchColourClassification(BaseModel):
    couch_colour: str = Field(description="The classified color of the couch")

# Define the prompt for zero-shot classification
PROMPT = """
You will see a still from a video. What color is the couch in the image? Use a single word to describe the color, e.g. 'white', 'black', 'grey', 'beige', 'blue', 'green', 'red', 'brown', 'purple', 'yellow', 'orange', 'pink'. If the couch has multiple colors, choose the most prominent one. 
"""

def get_couch_colour(video_id: str) -> dict:
    """
    Classify the couch color in a specified video.
    
    Parameters:
    - video_id (str): Unique identifier for the video.
    
    Returns:
    - dict: JSON object with classified color and video ID, or None if an error occurs.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": IMAGE_URL_TEMPLATE.format(video_id=video_id)
                            },
                        }
                    ],
                },
            ],
            response_format=CouchColourClassification,
            max_tokens=2000,
        )

        # Parse response content and add video_id
        json_object = json.loads(response.choices[0].message.content)
        json_object["video_id"] = video_id

        # Save the result in the 'classifications' directory
        save_path = os.path.join(CLASSIFICATIONS_DIR, f"{video_id}.json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as json_file:
            json.dump(json_object, json_file, indent=4, ensure_ascii=False)

        return json_object

    except (BadRequestError, APIError, OpenAIError) as e:
        logging.error(f"{e.__class__.__name__} for video {video_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error for video {video_id}: {e}")

    return None

def classify_couches(limit: int = 10):
    """
    Classify the color of couches in a set of videos.

    Parameters:
    - limit (int): Maximum number of videos to classify.
    """
    try:
        with open(VIDEO_LIST_PATH, "r") as couches_file:
            couches_to_classify = json.load(couches_file)
        couches_to_classify = [couch for couch in couches_to_classify.values() if couch.get("couch_detected")]

        logging.info(f"Found {len(couches_to_classify)} couches to classify.")

        for counter, couch in enumerate(couches_to_classify, start=1):
            if counter > limit:
                logging.info(f"Processed {limit} couches, stopping.")
                break

            video_id = couch.get("video_id")
            classification_path = os.path.join(CLASSIFICATIONS_DIR, f"{video_id}.json")

            if os.path.exists(classification_path):
                continue

            logging.info(f"Classifying couch with video_id {video_id}")
            json_object = get_couch_colour(video_id)
            logging.info(f"Saved classification for video_id {video_id}: {json_object}")

    except FileNotFoundError:
        logging.error(f"Video list file {VIDEO_LIST_PATH} not found.")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from couch information file.")

# Run the classification function
if __name__ == "__main__":
    classify_couches(limit=1e10)
