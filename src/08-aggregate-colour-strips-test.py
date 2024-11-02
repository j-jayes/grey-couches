import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import KMeans
from collections import Counter
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_weighted_colors(image_path, n_colors=1):
    logging.info(f"Processing image: {image_path}")
    
    # Load the image and reshape it
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
    pixels = image.reshape(-1, 3)

    # Exclude black pixels (background)
    non_black_pixels = pixels[np.any(pixels > 30, axis=1)]  # Exclude pixels that are too dark

    # Perform KMeans clustering to find dominant colors
    kmeans = KMeans(n_clusters=n_colors)
    kmeans.fit(non_black_pixels)
    labels = kmeans.labels_

    # Count pixel occurrences for each color
    label_counts = Counter(labels)
    total_count = sum(label_counts.values())

    # Get colors and their proportions
    colors = kmeans.cluster_centers_
    proportions = [label_counts[i] / total_count for i in range(n_colors)]

    # Convert colors to hex format for plotting
    hex_colors = [mcolors.to_hex(colors[i] / 255) for i in range(n_colors)]

    # Sort colors by hue, saturation, and brightness for smoother transitions
    hsv_colors = [mcolors.rgb_to_hsv(colors[i] / 255) for i in range(n_colors)]
    sorted_indices = sorted(range(n_colors), key=lambda x: (hsv_colors[x][0], hsv_colors[x][1], hsv_colors[x][2]))
    
    sorted_hex_colors = [hex_colors[i] for i in sorted_indices]
    sorted_proportions = [proportions[i] for i in sorted_indices]

    logging.info(f"Colors extracted: {sorted_hex_colors} with proportions: {sorted_proportions}")
    return sorted_hex_colors, sorted_proportions

def create_color_square(hex_colors, proportions, square_size=100):
    logging.info(f"Creating color square with colors: {hex_colors} and proportions: {proportions}")
    
    # Create a square image for a single couch
    square = np.zeros((square_size, square_size, 3), dtype=np.uint8)
    y_position = 0
    for color, proportion in zip(hex_colors, proportions):
        color_rgb = mcolors.hex2color(color)
        color_rgb = tuple(int(c * 255) for c in color_rgb)
        h = int(square_size * proportion)
        square[y_position:y_position + h, :, :] = color_rgb
        y_position += h
    return square

# Paths
input_dir = "data/couch_images_segmented"
output_dir = "data/couch_images_segmented_aggregated"
os.makedirs(output_dir, exist_ok=True)

# Parameters for grid layout
num_columns = 10  # Set the number of columns in the grid
square_size = 100  # Size of each square representing a couch

# Process each image to get color squares and sorting key
couch_squares = []
for filename in os.listdir(input_dir):
    if filename.endswith(".jpg"):
        video_id = os.path.splitext(filename)[0]
        image_path = os.path.join(input_dir, filename)
        
        # Get weighted colors and proportions
        hex_colors, proportions = get_weighted_colors(image_path, n_colors=1)
        
        # Generate color square image
        square = create_color_square(hex_colors, proportions, square_size=square_size)
        
        # Determine sorting key based on dominant color's HSV values
        dominant_color_index = proportions.index(max(proportions))
        dominant_hex_color = hex_colors[dominant_color_index]
        dominant_hsv = mcolors.rgb_to_hsv(mcolors.hex2color(dominant_hex_color))
        
        # Append square and sorting information
        couch_squares.append((dominant_hsv, square, video_id))

# Sort couch squares by hue, then saturation, then brightness
couch_squares.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]))

# Calculate grid dimensions
num_rows = (len(couch_squares) + num_columns - 1) // num_columns
composite_image = np.zeros((num_rows * square_size, num_columns * square_size, 3), dtype=np.uint8)

# Place each square in the composite image
for i, (_, square, video_id) in enumerate(couch_squares):
    row = i // num_columns
    col = i % num_columns
    composite_image[row * square_size:(row + 1) * square_size, col * square_size:(col + 1) * square_size] = square

# Save the composite grid image
composite_output_path = os.path.join(output_dir, "couch_color_grid_sorted.jpg")
Image.fromarray(composite_image).save(composite_output_path)
print(f"Composite grid image saved to {composite_output_path}")
