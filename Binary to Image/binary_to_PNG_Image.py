import numpy as np
import matplotlib.pyplot as plt
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

def convertBinary2GreyScaleImage(input_file, output_file, scale=None):
    """
    Convert binary file to a grayscale image representation.
    """
    with open(input_file, 'rb') as f:
        data = f.read()
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    width, height = get_size(len(data_array))
    
    padded_data = np.pad(data_array, (0, width * height - len(data_array)), mode='constant')
    image_data = padded_data.reshape((height, width))
    
    img = Image.fromarray(image_data, mode='L')
    if scale:
        img = img.resize(scale, Image.NEAREST)
    img.save(output_file)
    print(f"Grayscale image saved to {output_file}")

def convertBinary2RGBImage(input_file, output_file, scale=None):
    """
    Convert binary file to an RGB image representation.
    """
    with open(input_file, 'rb') as f:
        data = f.read()
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    width, height = get_size(len(data_array) // 3)
    
    padded_data = np.pad(data_array, (0, width * height * 3 - len(data_array)), mode='constant')
    image_data = padded_data.reshape((height, width, 3))
    
    img = Image.fromarray(image_data, mode='RGB')
    if scale:
        img = img.resize(scale, Image.NEAREST)
    img.save(output_file)
    print(f"RGB image saved to {output_file}")

def convertDirectoryBinaries(directory):
    """
    Convert all binary files in a directory to both RGB and grayscale images in PNG and SVG formats.
    """
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            base_name, _ = os.path.splitext(filename)
            convertBinary2RGBImage(file_path, os.path.join(directory, f"{base_name}_RGB.png"))
            convertBinary2GreyScaleImage(file_path, os.path.join(directory, f"{base_name}_Grayscale.png"))

# Example Usage
if __name__ == "__main__":
    convertDirectoryBinaries("/path/of/binaries/")