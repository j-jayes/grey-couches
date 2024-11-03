from PIL import Image, ImageSequence
import numpy as np

# Load the image
image_path = 'data/couch_images_segmented_aggregated/couch_color_composite_by_family.jpg'
image = Image.open(image_path)

# Define parameters for the GIF
window_height = 150
scroll_step = 5  # Amount to move the window down for each frame
frames = []

# Generate frames for the GIF
for y_offset in range(0, image.height - window_height, scroll_step):
    # Crop the current window section from the image
    frame = image.crop((0, y_offset, image.width, y_offset + window_height))
    frames.append(frame)

# Save the frames as a GIF
output_gif_path = 'assets/scrolled_couch_colors.gif'
frames[0].save(output_gif_path, format='GIF', append_images=frames[1:], save_all=True, duration=100, loop=0)
