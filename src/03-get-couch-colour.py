from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, BadRequestError, OpenAIError
import os
import json
import logging


# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

class CouchColourClassification(BaseModel):

    couch_colour: str = Field()

# Craft the prompt for zero-shot classification
prompt = f"""
You will see a still from a video. What colour is the couch in the image?
"""

def get_couch_colour(video_id):
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"https://github.com/j-jayes/grey-couches/blob/main/data/couch_images/{video_id}_couch.jpg?raw=true",
                            }
                        },
                    ]
                },
            ],
            response_format=CouchColourClassification,
            max_tokens=2000,
        )

        # Load the response into a JSON object
        json_object = json.loads(response.choices[0].message.content)

        # Add doc_id to the JSON object
        json_object['video_id'] = video_id

        # Ensure the directory structure exists
        save_path = f"classifications/{video_id}.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the JSON object
        with open(save_path, 'w') as json_file:
            json.dump(json_object, json_file, indent=4, ensure_ascii=False)

        return json_object

    except BadRequestError as e:
        logging.error(f"BadRequestError for video {video_id}: {str(e)}")
    except APIError as e:
        logging.error(f"APIError for video {video_id}: {str(e)}")
    except OpenAIError as e:
        logging.error(f"OpenAIError for video {video_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error for video {video_id}: {str(e)}")

    return None

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')



def classify_couches(limit=10):
    # Path to the file containing the list of documents to classify
    video_list_path = "data/couch_info.json"

    # Load the document list
    with open(video_list_path, 'r') as couches_file:
        couches_to_classify = json.load(couches_file)

    # filter out all couches where couch_detected is False
    # filter out all couches where couch_detected is False
    couches_to_classify = [couch for couch in couches_to_classify.values() if couch.get('couch_detected')]
    logging.info(f"Found {len(couches_to_classify)} couches to classify.")

    # Initialize counter
    counter = 0

    # Loop over each document in the list
    for couch in couches_to_classify:
        # Stop after processing the first 10 couches
        if counter >= limit:
            logging.info(f"Processed {limit} couches, stopping.")
            break

        # Use pdf_hash as a unique ID, as doc_id might not exist
        video_id = couch.get('video_id')

        # Define the path where the classification should be stored
        classification_path = f"classifications/{video_id}.json"

        # Check if the classification file already exists
        if os.path.exists(classification_path):
            # logging.info(f"Classification for video_id {video_id} already exists, skipping.")
            continue

        # If the classification doesn't exist, classify the document
        logging.info(f"Classifying document with video_id {video_id}")

        # Placeholder for the actual classification logic, to be replaced by real classification function
        json_object = get_couch_colour(video_id)

        logging.info(f"Saved classification for video_id {video_id} to {classification_path} as {json_object}.")

        # Increment counter after processing each document
        counter += 1


# Test the classification function
classify_couches(limit=5)
