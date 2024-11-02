"""
This file processes the couch images extracted from the Never Too Small videos and segments the couches from the background.

It does this by using a pre-trained YOLOv8 model for segmentation and then extracts the dominant colors from the segmented couch area.

It currently also saves the segmented couch images and the dominant colors in hex format to separate directories.

I think we will remove the hex values and the segmented images from the final version of the code, as they are not needed for the final visualization.

"""

import json
import os
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load YOLOv8 model
model = YOLO('yolov8n-seg.pt')  # Ensure you have the segmentation model for YOLO

def process_couch_image(video_id):
    # Load couch information JSON
    with open('data/couch_info.json', 'r') as f:
        couch_info = json.load(f)

    # Check if video_id exists in couch_info and if the couch is detected
    if video_id not in couch_info or not couch_info[video_id].get('couch_detected'):
        print(f"No couch detected for video ID: {video_id}")
        return
    
    # Define paths for the input image, output segmented image, and output hex values
    image_path = couch_info[video_id]['image_path']
    segmented_image_path = f"data/couch_images_segmented/{video_id}.jpg"
    hex_values_path = f"data/couch_hex_values/{video_id}.json"

    # ensure that the directories exist
    os.makedirs(os.path.dirname(segmented_image_path), exist_ok=True)
    os.makedirs(os.path.dirname(hex_values_path), exist_ok=True)

    # Check if segmented image and hex values already exist
    if os.path.exists(segmented_image_path) and os.path.exists(hex_values_path):
        print(f"Segmented image and hex values already exist for video ID: {video_id}")
        return
    
    # Load the image
    image = Image.open(image_path)
    image_np = np.array(image)

    # Perform inference with YOLOv8 model
    results = model(image_np)

    # Check if masks are available in the results
    if not hasattr(results[0], 'masks') or results[0].masks is None:
        print("No segmentation masks found in the results.")
        return

    # Extract the segmentation mask for the couch
    couch_mask = None
    for seg, cls in zip(results[0].masks.data, results[0].boxes.cls):
        label_name = results[0].names[int(cls)]
        if label_name == 'couch':  # Look for the 'couch' label
            couch_mask = seg.cpu().numpy()
            break

    if couch_mask is None:
        print("Couch not detected in the image.")
        return

    # Ensure the mask is in uint8 format for OpenCV
    couch_mask = (couch_mask * 255).astype(np.uint8)
    if couch_mask.shape != image_np.shape[:2]:  # Ensure mask has same dimensions as source image
        couch_mask = cv2.resize(couch_mask, (image_np.shape[1], image_np.shape[0]))

    # Apply the mask to the original image
    segmented_couch = cv2.bitwise_and(image_np, image_np, mask=couch_mask)

    # Reshape the segmented part for clustering
    pixels = segmented_couch.reshape((-1, 3))
    pixels = pixels[np.all(pixels != [0, 0, 0], axis=1)]  # Exclude black areas (non-couch)

    # Use KMeans clustering to find the dominant colors
    n_colors = 5
    kmeans = KMeans(n_clusters=n_colors)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_

    # Convert colors to hex format
    hex_colors = ['#%02x%02x%02x' % tuple(map(int, color)) for color in colors]

    # Save segmented couch image
    Image.fromarray(segmented_couch).save(segmented_image_path)
    print(f"Segmented image saved to {segmented_image_path}")

    # Save hex colors to JSON
    with open(hex_values_path, 'w') as f:
        json.dump(hex_colors, f)
    print(f"Hex values saved to {hex_values_path}")

# loop through all of the couches in the couch_info.json file
with open('data/couch_info.json', 'r') as f:
    couch_info = json.load(f)

for video_id in couch_info:
    process_couch_image(video_id)