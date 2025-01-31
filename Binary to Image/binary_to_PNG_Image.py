import numpy as np
import matplotlib.pyplot as plt
import os
import math
from PIL import Image
from queue import Queue
from threading import Thread
import argparse
import sys

def read_binary_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

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
    data = read_binary_file(input_file)
    
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
    data = read_binary_file(input_file)
    
    data_array = np.frombuffer(data, dtype=np.uint8)
    width, height = get_size(len(data_array) // 3)
    
    padded_data = np.pad(data_array, (0, width * height * 3 - len(data_array)), mode='constant')
    image_data = padded_data.reshape((height, width, 3))
    
    img = Image.fromarray(image_data, mode='RGB')
    if scale:
        img = img.resize(scale, Image.NEAREST)
    img.save(output_file)
    print(f"RGB image saved to {output_file}")

def run(file_queue, width):
    while not file_queue.empty():
        file_path = file_queue.get()
        base_name, _ = os.path.splitext(file_path)
        directory = os.path.dirname(file_path)
        convertBinary2RGBImage(file_path, os.path.join(directory, f"{base_name}_RGB.png"))
        convertBinary2GreyScaleImage(file_path, os.path.join(directory, f"{base_name}_Grayscale.png"))
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
    parser = argparse.ArgumentParser(prog='binary_to_PNG_Image.py', description="Convert binary file to SVG image")
    parser.add_argument('input_dir', help='Input directory path is which include executable files')
    parser.add_argument('thread_number', help='number of operation threads')
    args = parser.parse_args()
    main(args.input_dir, int(args.thread_number), width=None)