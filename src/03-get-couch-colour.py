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



class DocumentClassification(BaseModel):

    document_title_english: str = Field()



# Craft the prompt for zero-shot classification
prompt = f"""
You are an expert public finance document classification system.

You know about the different types of public finance documents in African countries, including English, French, Portuguese, Arabic and Spanish-speaking countries.

You will be provided with a schema on how to classify documents based on their content and metadata.

Classify the document based on the provided information and text from the image. If it does not fit a specific category, or is not a public finance document, select 'Other'.
"""

def get_document_classification(doc_id, filename):
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
                        {"type": "text", "text": "Here is the classification schema"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://github.com/j-jayes/sandbox/blob/main/images/cabri_budget_doc_schema.png?raw=true",
                            }
                        },
                        {"type": "text", "text": f"Here is the document to classify, with filename{filename}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"https://github.com/j-jayes/sandbox/blob/main/images_2nd_update/{doc_id}.png?raw=true",
                            }
                        },
                    ]
                },
            ],
            response_format=DocumentClassification,
            max_tokens=2000,
        )

        # Load the response into a JSON object
        json_object = json.loads(response.choices[0].message.content)

        # Add doc_id to the JSON object
        json_object['doc_id'] = doc_id

        # Ensure the directory structure exists
        save_path = f"classifications/pass_4/{doc_id}.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the JSON object
        with open(save_path, 'w') as json_file:
            json.dump(json_object, json_file, indent=4, ensure_ascii=False)

        return json_object

    except BadRequestError as e:
        logging.error(f"BadRequestError for document {doc_id}: {str(e)}")
    except APIError as e:
        logging.error(f"APIError for document {doc_id}: {str(e)}")
    except OpenAIError as e:
        logging.error(f"OpenAIError for document {doc_id}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error for document {doc_id}: {str(e)}")

    return None
