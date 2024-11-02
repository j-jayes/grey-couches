import os
import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import yt_dlp
import numpy as np
import json

# Configurable variables
MODEL_NAME = "kadirnar/Yolov10/yolov10n.pt"
FRAME_INTERVAL = 100  # Process every nth frame
COUCH_CLASS = 'couch'
CONFIDENCE_THRESHOLD = 0.7
OUTPUT_DIR = "data/couch_images"
VIDEO_DIR = "videos"
INFO_FILE_PATH = "data/couch_info.json"
VIDEO_IDS_FILE = "data/never_too_small_official_playlist.json"

def setup_directories():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_video(video_id: str) -> str:
    video_path = os.path.join(VIDEO_DIR, f"{video_id}.mp4")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': '137+140',
        'outtmpl': video_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    return video_path

def load_model(model_name: str):
    return YOLO(model_name)

def process_frame(frame, model):
    results = model(frame)
    for result in results:
        for box in result.boxes:
            if result.names[int(box.cls[0])] == COUCH_CLASS and box.conf[0] > CONFIDENCE_THRESHOLD:
                x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                box_area = (x_max - x_min) * (y_max - y_min)
                frame_area = frame.shape[0] * frame.shape[1]
                box_ratio = box_area / frame_area
                return box_ratio, frame
    return None, None

def find_best_frame(video_path: str, model, frame_interval: int):
    cap = cv2.VideoCapture(video_path)
    best_frame = None
    largest_box_ratio = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            box_ratio, detected_frame = process_frame(frame, model)
            if box_ratio and box_ratio > largest_box_ratio:
                largest_box_ratio = box_ratio
                best_frame = detected_frame.copy()
        frame_count += frame_interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)

    cap.release()
    return best_frame, largest_box_ratio

def display_frame(frame, box_ratio):
    if frame is not None:
        plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.title(f"Largest Couch Detection (Ratio: {box_ratio:.2f})")
        plt.show()
    else:
        print("No couch detected with confidence above the threshold.")

def save_frame(frame, video_id: str):
    output_path = os.path.join(OUTPUT_DIR, f"{video_id}_couch.jpg")
    if frame is not None:
        cv2.imwrite(output_path, frame)
        print(f"Saved the largest couch detection frame to {output_path}")
        return output_path
    else:
        print("No frame to save.")
        return None

def save_detection_info(video_id: str, detected: bool, image_path: str):
    info = {
        "video_id": video_id,
        "couch_detected": detected,
        "image_path": image_path if detected else None
    }
    
    # Load existing data if it exists
    if os.path.exists(INFO_FILE_PATH):
        with open(INFO_FILE_PATH, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Update the entry for the current video
    data[video_id] = info

    # Write updated data back to JSON file
    with open(INFO_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Detection info saved to {INFO_FILE_PATH}")

def main():
    setup_directories()
    model = load_model(MODEL_NAME)
    
    # Load video IDs from JSON file
    with open(VIDEO_IDS_FILE, "r") as f:
        video_entries = json.load(f)
    
    video_ids = [entry['id'] for entry in video_entries]
    
    # Load existing detection info if it exists
    if os.path.exists(INFO_FILE_PATH):
        with open(INFO_FILE_PATH, "r") as f:
            existing_info = json.load(f)
    else:
        existing_info = {}

    for video_id in video_ids:
        if video_id in existing_info:
            print(f"Skipping video {video_id} as it is already processed.")
            continue
        
        video_path = download_video(video_id)
        best_frame, largest_box_ratio = find_best_frame(video_path, model, FRAME_INTERVAL)
        
        # Save frame and get path if a couch is detected
        if best_frame is not None:
            # display_frame(best_frame, largest_box_ratio)
            image_path = save_frame(best_frame, video_id)
            save_detection_info(video_id, detected=True, image_path=image_path)
        else:
            print(f"No couch detected in video {video_id} with confidence above the threshold.")
            save_detection_info(video_id, detected=False, image_path=None)

if __name__ == "__main__":
    main()