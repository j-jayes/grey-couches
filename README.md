# Grey Couches

### Analyzing Couch Colors in Tiny Homes from the YouTube Channel *Never Too Small*

**Project Description**:
This project aims to analyze property videos from the popular YouTube channel *Never Too Small* to identify the color of couches featured in each video. *Never Too Small* showcases creative, small-footprint living solutions, with tiny apartments and micro homes designed by architects from around the world. The channel focuses on optimizing space while maintaining style and comfort, often including modern furniture choices such as couches. 

In this project, we are particularly interested in determining the share of properties that have **grey couches**, given their frequent appearance in minimalist designs. The process involves automatically downloading videos, detecting couches in video frames, analyzing their colors, and generating reports on the prevalence of grey couches across the videos.

**Technologies Used**:
- Video extraction: `pytube`, `ffmpeg`
- Object detection: YOLO / OpenCV
- Color analysis: `opencv`, `scikit-learn`, `webcolors`
- Reporting: Python libraries (`matplotlib`, `PIL`)

**Goal**:
To analyze the proportion of properties in *Never Too Small* videos that feature grey couches, contributing to a better understanding of design trends in small-space living.

This project supports a data-driven approach to interior design, with a focus on analyzing trends in the use of color in modern, space-efficient furniture.

### Problem Breakdown: Analyzing YouTube Videos to Identify Couch Colors

To identify the color of couches in property videos on YouTube, the process can be broken down into several key steps. Each part involves distinct tasks, such as video analysis, image extraction, and color identification. Below is a breakdown of the process and a project specification.

#### 1. **Video Collection**:
   - **Input**: YouTube video URL(s) of property walkthroughs.
   - **Goal**: Extract video frames where the couch appears, to later analyze the color.

   **Sub-tasks**:
   - Automate video downloading from YouTube (e.g., using `pytube` or `youtube-dl`).
   - Define criteria for frame selection (e.g., every second, when a couch is likely to appear).
   - Ensure compliance with YouTube’s terms of service.

#### 2. **Object Detection**:
   - **Input**: Frames from the video.
   - **Goal**: Automatically detect the presence of a couch in each frame.
   
   **Sub-tasks**:
   - Use an object detection model (e.g., YOLO, OpenCV’s pre-trained models, or Google Cloud Vision) to identify couches in the frames.
   - Fine-tune detection accuracy for different couch styles and ensure that irrelevant objects (e.g., chairs or tables) are not identified as couches.

#### 3. **Frame Selection**:
   - **Input**: Frames with a detected couch.
   - **Goal**: Select the clearest frames where the couch is fully visible.

   **Sub-tasks**:
   - Filter out frames where the couch is partially visible or blocked by other objects.
   - Prioritize frames with good lighting and minimal obstructions.

#### 4. **Color Identification**:
   - **Input**: Selected frames of the couch.
   - **Goal**: Analyze the predominant colors of the couch in each frame.

   **Sub-tasks**:
   - Use color analysis techniques (e.g., `KMeans` clustering in Python’s `opencv` or `scikit-learn`) to identify dominant colors in the frame.
   - Map the RGB values of identified colors to human-readable names using color libraries (e.g., `webcolors`).
   - Consider multiple frames to average out lighting variations or reflections.

#### 5. **Reporting and Output**:
   - **Input**: Identified couch colors from the frames.
   - **Goal**: Generate a report summarizing the detected couch color(s) for each video.

   **Sub-tasks**:
   - Provide a summary of the dominant couch colors (including shades) for each analyzed video.
   - Optionally, include visual representations (like pie charts) showing color distributions in the frames.

---

### Project Specification: Couch Color Detection from YouTube Videos

**Objective**: 
To develop a system that analyzes YouTube property walkthrough videos to identify the color of couches within the video frames.

---

#### **Project Components**:

1. **Video Input and Frame Extraction**:
   - **Tooling**: `pytube`, `youtube-dl` for video downloads.
   - **Functionality**: Automatically download videos from YouTube and split them into frames.
   - **Output**: Extracted frames for further analysis.

2. **Couch Detection**:
   - **Tooling**: Pre-trained object detection models like YOLO or OpenCV’s Haar Cascades.
   - **Functionality**: Detect the presence of couches in each frame.
   - **Output**: Frames where a couch has been detected, with bounding boxes around the object.

3. **Color Analysis**:
   - **Tooling**: `opencv` and `scikit-learn` for color clustering, `webcolors` for mapping RGB values.
   - **Functionality**: Analyze the dominant colors of the detected couches in the selected frames.
   - **Output**: List of identified colors (e.g., beige, dark gray, etc.), including RGB and color name.

4. **Lighting and Frame Selection**:
   - **Tooling**: Custom filtering based on frame properties (e.g., brightness, clarity).
   - **Functionality**: Select the best frames for analysis based on lighting and visibility.
   - **Output**: Set of optimal frames for color extraction.

5. **Reporting and Visualization**:
   - **Tooling**: Python libraries for reporting (e.g., `matplotlib`, `PIL` for images).
   - **Functionality**: Generate a summary report of detected couch colors.
   - **Output**: A PDF or text-based report, including color information, example frames, and pie charts representing the color distribution.

---

#### **Tools and Libraries**:
- **Video Downloading**: `pytube`, `youtube-dl`
- **Frame Extraction**: `ffmpeg`, `opencv`
- **Object Detection**: YOLO, Google Cloud Vision API, `opencv`
- **Color Identification**: `opencv`, `scikit-learn`, `webcolors`
- **Reporting**: `matplotlib`, `PIL`

#### **Optional Features**:
- Real-time video processing (if the system needs to work on live streams).
- Handle multiple objects in the frame (if there are multiple couches or other objects).
- Incorporate a confidence threshold for color detection.
