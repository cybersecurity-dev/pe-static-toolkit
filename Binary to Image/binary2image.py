import os
import math
from PIL import Image

def get_size(data_length, width=None):
    if width is None:  # If no width is specified
        size = data_length
        if size < 10240:
            width = 32
        elif 10240 <= size <= 10240 * 3:
            width = 64
        elif 10240 * 3 <= size <= 10240 * 6:
            width = 128
        elif 10240 * 6 <= size <= 10240 * 10:
            width = 256
        elif 10240 * 10 <= size <= 10240 * 20:
            width = 384
        elif 10240 * 20 <= size <= 10240 * 50:
            width = 512
        elif 10240 * 50 <= size <= 10240 * 100:
            width = 768
        else:
            width = 1024
        height = int(size / width) + 1
    else:
        width = int(math.sqrt(data_length)) + 1
        height = width
    return (width, height)

#Convert binary file to an image representation.
def binary_to_image(input_file, output_file, mode='RGB', scale=None):
    """   
    :param input_file: Path to the binary file.
    :param output_file: Path to save the output image (PNG or SVG).
    :param mode: 'RGB' for color or 'L' for grayscale.
    :param scale: Resize scale (tuple width, height) or None for automatic.
    """
    with open(input_file, 'rb') as f:
        data = f.read()
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    
    # Determine image dimensions
    width, height = get_size(len(data_array) // (3 if mode == 'RGB' else 1))
    
    if mode == 'RGB':
        padded_data = np.pad(data_array, (0, width * height * 3 - len(data_array)), mode='constant')
        image_data = padded_data.reshape((height, width, 3))
    else:  # Grayscale
        padded_data = np.pad(data_array, (0, width * height - len(data_array)), mode='constant')
        image_data = padded_data.reshape((height, width))
    
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