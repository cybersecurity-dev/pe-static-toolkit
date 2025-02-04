import os, time
import argparse
import sys
import numpy as np
import svgwrite
from queue import Queue
from threading import Thread

def read_binary_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def bytes_to_rgb(bytes_data, width=None):
    # Calculate dimensions
    size = len(bytes_data)
    if width is None:
        width = int(np.ceil(np.sqrt(size / 3)))  # Rough estimate
    height = int(np.ceil(size / (width * 3)))
    
    # Create an empty array of the right size, padded with zeros if necessary
    rgb_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    idx = 0
    for i in range(height):
        for j in range(width):
            if idx + 2 < size:  # Ensure we have at least 3 bytes left
                rgb_array[i, j] = [bytes_data[idx], bytes_data[idx + 1], bytes_data[idx + 2]]
                idx += 3
            else:
                # Pad with zeros if not enough bytes left
                rgb_array[i, j] = [0, 0, 0]
    
    return rgb_array, width, height

def bytes_to_grayscale(bytes_data, width=None):
    # Convert bytes to grayscale values
    size = len(bytes_data)
    if width is None:
        width = int(np.ceil(np.sqrt(size)))  # Rough estimate
    height = int(np.ceil(size / width))
    
    # Create an empty array of the right size, padded with zeros if necessary
    gray_array = np.zeros((height, width), dtype=np.uint8)
    
    idx = 0
    for i in range(height):
        for j in range(width):
            if idx < size:
                gray_array[i, j] = bytes_data[idx]
                idx += 1
            else:
                # Pad with zeros if not enough bytes left
                gray_array[i, j] = 0
    
    return gray_array, width, height

def create_svg_rgb(rgb_array, output_file, width=500, height=500):
    dwg = svgwrite.Drawing(output_file, size=(width, height))
    cell_width = width / rgb_array.shape[1]
    cell_height = height / rgb_array.shape[0]
    
    for y in range(rgb_array.shape[0]):
        for x in range(rgb_array.shape[1]):
            color = '#{:02x}{:02x}{:02x}'.format(*rgb_array[y, x])
            dwg.add(dwg.rect(insert=(x * cell_width, y * cell_height),
                             size=(cell_width, cell_height),
                             fill=color))
    
    dwg.save()

def create_svg_grayscale(gray_array, output_file, width=500, height=500):
    dwg = svgwrite.Drawing(output_file, size=(width, height))
    cell_width = width / gray_array.shape[1]
    cell_height = height / gray_array.shape[0]
    
    for y in range(gray_array.shape[0]):
        for x in range(gray_array.shape[1]):
            gray_value = gray_array[y, x]
            color = '#{:02x}{:02x}{:02x}'.format(gray_value, gray_value, gray_value)
            dwg.add(dwg.rect(insert=(x * cell_width, y * cell_height),
                             size=(cell_width, cell_height),
                             fill=color))
    
    dwg.save()

def convertBinary2GreyScaleImage(input_file, output_file, scale=None):
    """
    Convert binary file to a grayscale image representation.
    """
    # Convert to Grayscale image
    bytes_data = read_binary_file(input_file)
    gray_array, gray_width, gray_height = bytes_to_grayscale(bytes_data)
    create_svg_grayscale(gray_array, output_file, width=gray_width*10, height=gray_height*10)

def convertBinary2RGBImage(input_file, output_file, scale=None):
    """
    Convert binary file to an RGB image representation.
    """
    # Convert to RGB image
    bytes_data = read_binary_file(input_file)
    rgb_array, rgb_width, rgb_height = bytes_to_rgb(bytes_data)
    create_svg_rgb(rgb_array, output_file, width=rgb_width*10, height=rgb_height*10)


def run(file_queue, width):
    while not file_queue.empty():
        file_path = file_queue.get()
        base_name, _ = os.path.splitext(file_path)
        directory = os.path.dirname(file_path)
        convertBinary2RGBImage(file_path, os.path.join(directory, f"{base_name}_RGB.svg"))
        convertBinary2GreyScaleImage(file_path, os.path.join(directory, f"{base_name}_Grayscale.svg"))
        file_queue.task_done()


def main(input_dir, thread_number=2, width=None):
	# Get all executable files in input directory and add them into queue
    file_queue = Queue()
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            base_name, _ = os.path.splitext(filename)
            file_queue.put(file_path)

	# Start thread
    for index in range(thread_number):
        thread = Thread(target=run, args=(file_queue, width))
        thread.daemon = True
        thread.start()
    file_queue.join()

if __name__ == '__main__':
    print("[" + __file__ + "]'s last modified: %s" % time.ctime(os.path.getmtime(__file__)))
    # Check if a parameter is provided
    parser = argparse.ArgumentParser(prog='binary_to_SVG_Image.py', description="Convert binary file to SVG image")
    parser.add_argument('input_dir', help='Input directory path is which include executable files')
    parser.add_argument('thread_number', help='number of operation threads')
    args = parser.parse_args()
    main(args.input_dir, int(args.thread_number), width=None)