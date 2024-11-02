"""
This file creates a type of colour strip for the most common colours found in the couch images extracted from the Never Too Small videos.
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import KMeans
from collections import Counter

def get_weighted_colors(image_path, n_colors=5):
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

    # Sort colors by hue for a smoother gradient effect
    hsv_colors = [mcolors.rgb_to_hsv(colors[i] / 255) for i in range(n_colors)]
    sorted_indices = sorted(range(n_colors), key=lambda x: (hsv_colors[x][0], hsv_colors[x][1], hsv_colors[x][2]))
    
    sorted_hex_colors = [hex_colors[i] for i in sorted_indices]
    sorted_proportions = [proportions[i] for i in sorted_indices]

    return sorted_hex_colors, sorted_proportions

def plot_weighted_color_strip(hex_colors, proportions, output_path):
    # Plot color strip with proportional widths
    fig, ax = plt.subplots(figsize=(12, 2))
    x_position = 0
    for color, proportion in zip(hex_colors, proportions):
        width = proportion  # Proportional width for each color
        ax.add_patch(plt.Rectangle((x_position, 0), width, 1, color=color))
        x_position += width

    # Remove axis for a cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Weighted Color Strip of Most Common Couch Colors")
    
    # Save the plot
    plt.savefig(output_path)
    plt.close(fig)
    print(f"Saved color strip to {output_path}")

# Paths
input_dir = "data/couch_images_segmented"
output_dir = "data/couch_images_segmented_colour_strips"
os.makedirs(output_dir, exist_ok=True)

# Process each image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".jpg"):
        video_id = os.path.splitext(filename)[0]
        image_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"{video_id}.jpg")
        
        # Get weighted colors and proportions
        hex_colors, proportions = get_weighted_colors(image_path, n_colors=5)
        
        # Plot and save the weighted color strip
        plot_weighted_color_strip(hex_colors, proportions, output_path)
