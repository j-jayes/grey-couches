import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import KMeans
from collections import Counter
from PIL import Image

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

    # Sort colors by hue, saturation, and brightness for smoother transitions
    hsv_colors = [mcolors.rgb_to_hsv(colors[i] / 255) for i in range(n_colors)]
    sorted_indices = sorted(range(n_colors), key=lambda x: (hsv_colors[x][0], hsv_colors[x][1], hsv_colors[x][2]))
    
    sorted_hex_colors = [hex_colors[i] for i in sorted_indices]
    sorted_proportions = [proportions[i] for i in sorted_indices]

    return sorted_hex_colors, sorted_proportions

def plot_color_strip(hex_colors, proportions, width=300, height=50):
    # Create an image strip for a single couch
    strip = np.zeros((height, width, 3), dtype=np.uint8)
    x_position = 0
    for color, proportion in zip(hex_colors, proportions):
        color_rgb = mcolors.hex2color(color)
        color_rgb = tuple(int(c * 255) for c in color_rgb)
        w = int(width * proportion)
        strip[:, x_position:x_position + w] = color_rgb
        x_position += w
    return strip

def assign_color_family(hsv):
    """Assigns a color family based on hue, saturation, and brightness."""
    h, s, v = hsv
    if s < 0.2 and v > 0.8:  # Light grey/white
        return 'Grey/White'
    elif s < 0.2 and v < 0.5:  # Dark grey/black
        return 'Dark Grey/Black'
    elif h < 0.05 or h > 0.95:  # Reds
        return 'Red'
    elif 0.05 <= h < 0.15:  # Oranges
        return 'Orange'
    elif 0.15 <= h < 0.35:  # Yellows/Browns
        return 'Yellow/Brown'
    elif 0.35 <= h < 0.5:  # Greens
        return 'Green'
    elif 0.5 <= h < 0.65:  # Cyans
        return 'Cyan'
    elif 0.65 <= h < 0.85:  # Blues
        return 'Blue'
    elif 0.85 <= h < 0.95:  # Purples
        return 'Purple'
    else:
        return 'Other'

# Paths
input_dir = "data/couch_images_segmented"
output_dir = "data/couch_images_segmented_aggregated"
os.makedirs(output_dir, exist_ok=True)

# Process each image to get color strips and sorting key
couch_strips = []
for filename in os.listdir(input_dir):
    if filename.endswith(".jpg"):
        video_id = os.path.splitext(filename)[0]
        image_path = os.path.join(input_dir, filename)
        
        # Get weighted colors and proportions
        hex_colors, proportions = get_weighted_colors(image_path, n_colors=5)
        
        # Generate color strip image
        strip = plot_color_strip(hex_colors, proportions, width=300, height=50)
        
        # Determine color family based on the dominant color
        dominant_color_index = proportions.index(max(proportions))
        dominant_hex_color = hex_colors[dominant_color_index]
        dominant_rgb = mcolors.hex2color(dominant_hex_color)
        dominant_hsv = mcolors.rgb_to_hsv(dominant_rgb)
        color_family = assign_color_family(dominant_hsv)
        
        # Append strip and sorting information
        couch_strips.append((color_family, dominant_hsv, strip, video_id))

# Sort couch strips by color family, then by hue and brightness within each family
couch_strips.sort(key=lambda x: (x[0], x[1][0], x[1][2]))

# Create a composite image with each strip as a row
strip_height = couch_strips[0][2].shape[0]
composite_height = strip_height * len(couch_strips)
composite_width = couch_strips[0][2].shape[1]
composite_image = np.zeros((composite_height, composite_width, 3), dtype=np.uint8)

# Stack each color strip as a row in the composite image
for i, (_, _, strip, video_id) in enumerate(couch_strips):
    composite_image[i * strip_height:(i + 1) * strip_height, :, :] = strip

# Save the composite image
composite_output_path = os.path.join(output_dir, "couch_color_composite_by_family.jpg")
Image.fromarray(composite_image).save(composite_output_path)
print(f"Composite image saved to {composite_output_path}")
