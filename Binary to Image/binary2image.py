import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image


def binary_to_image(input_file, output_file, mode='RGB', scale=None):
    """
    Convert binary file to an image representation.
    
    :param input_file: Path to the binary file.
    :param output_file: Path to save the output image (PNG or SVG).
    :param mode: 'RGB' for color or 'L' for grayscale.
    :param scale: Resize scale (tuple width, height) or None for automatic.
    """
    with open(input_file, 'rb') as f:
        data = f.read()
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    
    # Determine image dimensions (nearest square size)
    size = int(np.ceil(np.sqrt(len(data_array) / (3 if mode == 'RGB' else 1))))
    
    if mode == 'RGB':
        padded_data = np.pad(data_array, (0, size * size * 3 - len(data_array)), mode='constant')
        image_data = padded_data.reshape((size, size, 3))
    else:  # Grayscale
        padded_data = np.pad(data_array, (0, size * size - len(data_array)), mode='constant')
        image_data = padded_data.reshape((size, size))
    
    img = Image.fromarray(image_data, mode=mode)
    
    if scale:
        img = img.resize(scale, Image.NEAREST)
    
    # Save image
    if output_file.lower().endswith('.svg'):
        plt.imsave(output_file, image_data, cmap='gray' if mode == 'L' else None, format='svg')
    else:
        img.save(output_file)
    
    print(f"Image saved to {output_file}")

# Example Usage
if __name__ == "__main__":
    binary_to_image('test.exe', 'output.png', mode='RGB')  # Convert to PNG
    binary_to_image('test.exe', 'output.svg', mode='L')    # Convert to SVG (grayscale)