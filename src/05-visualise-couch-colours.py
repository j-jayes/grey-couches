"""
This file creates a type of colour swatch for the most common colours found in the couch images extracted from the Never Too Small videos.
"""


import json
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.colors as mcolors

# read in data/couch_info.json and filter out all couches where couch_detected is False
with open("data/couch_info.json", "r") as f:
    couches = json.load(f)

couches = [couch for couch in couches.values() if couch.get("couch_detected")]

# select only the video_id from the couches
video_ids = [couch["video_id"] for couch in couches]

video_id = "4i8WENruig0"

# Load hex values from all JSON files in data/couch_hex_values directory
hex_values = []

# loop over each video_id and load the hex values from the corresponding JSON file
for video_id in video_ids:
    hex_values_path = f"data/couch_hex_values/{video_id}.json"
    try:
        with open(hex_values_path, "r") as f:
            hex_data = json.load(f)
            hex_values.extend(hex_data)
    except FileNotFoundError:
        print(f"File not found: {hex_values_path}")




# Count occurrences of each color
color_counts = Counter(hex_values)
colors, counts = zip(*color_counts.items())


# Convert hex to RGB and then to HSV for sorting
rgb_colors = [mcolors.hex2color(color) for color in hex_values]
hsv_colors = [mcolors.rgb_to_hsv(color) for color in rgb_colors]

# Sort by hue, then saturation, then brightness
sorted_hsv_colors = sorted(hsv_colors, key=lambda x: (x[0], x[1], x[2]))
sorted_rgb_colors = [mcolors.hsv_to_rgb(color) for color in sorted_hsv_colors]
sorted_hex_colors = [mcolors.to_hex(color) for color in sorted_rgb_colors]

# Plot the sorted color strip
fig, ax = plt.subplots(figsize=(12, 2))
total_count = len(sorted_hex_colors)
x_position = 0
width = 1 / total_count

for color in sorted_hex_colors:
    ax.add_patch(plt.Rectangle((x_position, 0), width, 1, color=color))
    x_position += width

# Remove axis for a cleaner look
ax.set_xticks([])
ax.set_yticks([])
plt.title("Sorted Color Strip of Most Common Couch Colors")
plt.show()