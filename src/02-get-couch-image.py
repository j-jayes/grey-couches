import os
import cv2
import yt_dlp

# Inputs from GitHub Actions
video_url = os.getenv("VIDEO_URL")
video_id = os.getenv("VIDEO_ID")

video_url = "https://www.youtube.com/watch?v=yuPhS__2SMs&ab_channel=NEVERTOOSMALL"

# Set up paths
output_dir = os.path.join("images")
os.makedirs(output_dir, exist_ok=True)
frame_path = os.path.join(output_dir, f"{video_id}_frame100.jpg")
video_path = os.path.join(output_dir, f"{video_id}.mp4")

# Use yt-dlp to download video to a permanent file
ydl_opts = {
    'format': '137+140',
    'outtmpl': video_path,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

# Check if the video file exists and is not empty
if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
    # Open video file with OpenCV
    cap = cv2.VideoCapture(video_path)
    frame_number = 100  # Frame to extract

    # Move to the 100th frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(frame_path, frame)
        print(f"Saved frame {frame_number} to {frame_path}")
    else:
        print("Failed to capture frame.")

    # Release video capture and clean up
    cap.release()

    # Delete the video file
    os.remove(video_path)
    print(f"Deleted video file {video_path}")
else:
    print("Failed to download video or video file is empty.")