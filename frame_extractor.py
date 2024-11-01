import os
import cv2
from pytube import YouTube

# Fetch environment variables from GitHub Actions
video_url = os.getenv("VIDEO_URL")
video_id = os.getenv("VIDEO_ID")

# Directory to save the frame
image_dir = "images"
os.makedirs(image_dir, exist_ok=True)

def download_video(url):
    """Downloads video and returns the file path."""
    yt = YouTube(url)
    video_stream = yt.streams.filter(file_extension="mp4").first()
    return video_stream.download(filename="temp_video.mp4")

def save_frame(video_path, frame_number, output_path):
    """Extracts and saves the specified frame from the video."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Frame {frame_number} saved as {output_path}")
    else:
        print("Failed to capture frame.")
    cap.release()

def main():
    try:
        video_path = download_video(video_url)
        output_image_path = os.path.join(image_dir, f"{video_id}_frame100.jpg")
        
        # Save the 100th frame
        save_frame(video_path, 100, output_image_path)
        
    finally:
        # Cleanup: delete the downloaded video
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Temporary video file {video_path} removed.")

if __name__ == "__main__":
    main()
