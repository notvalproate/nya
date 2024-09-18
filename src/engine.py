from typing import List
from numpy.typing import NDArray

from PIL import Image
import numpy as np
import os
from bitarray import bitarray

class ImageData:
    width = int
    height = int
    pixels = np.array

    def __init__(self, path):
        img = Image.open(path)
        self.width, self.height = img.size
        img = img.convert("RGBA")
        self.pixels = np.array(img)

class NYA_HEADER:
    def __init__(self):
        self.ALPHA_ENCODING = False # ONE BIT
        self.VERTICAL_ENCODING = False # ONE BIT
        self.WIDTH = 0 # 16 BITS

class NYA_SINGLE:
    def __init__(self, value: NDArray[np.uint8]):
        pass

def nparray_to_nya_bytes(pixels: np.array, width: int, height: int) -> bytes:
    # STAGE 1: DECIDE BETWEEN 3 OR 4 CHANNELS

    NYA_ALPHA_EXISTS = False
    for row in pixels:
        for pixel in row:
            if pixel[3] != 255:
                NYA_ALPHA_EXISTS = True
                break

    previous = np.array([255, 255, 255, 255])

    if not NYA_ALPHA_EXISTS:
        pixels = pixels[:, :, :3]
        previous = np.array([255, 255, 255])

    # STAGE 2: APPLY THE DIFFERENCE FILTER

    for row in pixels:
        i = 0
        while i < len(row):
            diff = row[i] - previous
            previous = row[i].copy()
            row[i] = diff
            i += 1
    
    # STAGE 3: PERFORM RLE ENCODING AND STORE IT IN nya_pixels. nya_values WILL STORE THE COUNTS OF EACH DIFFERENCE/PIXEL

    nya_pixels = []
    nya_values = {}
    pixels = pixels.reshape(-1, pixels.shape[-1])
    

    # STAGE 4: PERFORM HUFFMAN ENCODING ON THE MOST COMMON 256 DIFFERENCES

    # STAGE 5: WRITE EVERYTHING TO A BITARRAY AND THEN RETURN THE BYTES

    pixels_flat = pixels.reshape(-1, pixels.shape[-1])
    pixels_data = bitarray(endian="big")

    i = 0
    previous_pixel = pixels_flat[0]
    pixel_count = len(pixels_flat)

    while i < pixel_count:
        count = 0

        while count <= 256 and i < pixel_count and np.array_equal(pixels_flat[i], previous_pixel):
            count += 1
            i += 1

        if count == 0:
            pixels_data.extend([0])

            pixels_data.frombytes(pixels_flat[i].tobytes())
            previous_pixel = pixels_flat[i]
        else:
            pixels_data.extend([1])

            adjusted_count = count - 1
            count_length = adjusted_count.bit_length()
            length_length = count_length.bit_length()

            count_str = f'{adjusted_count:0{count_length}b}'
            length_str = f'{length_length:03b}'

            # Add Length for 4 bits
            pixels_data.extend([int(bit) for bit in length_str])
            # Add Count for count_length bits
            pixels_data.extend([int(bit) for bit in count_str])

            i -+ 1
            
        i += 1

    return pixels_data.tobytes()
    
def convert_to_nya(image_path: str, output_dir: str) -> bool:
    image_data = ImageData(image_path)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        width_bytes = image_data.width.to_bytes(16, byteorder="big")
        height_bytes = image_data.height.to_bytes(16, byteorder="big")

        f.write(width_bytes)
        f.write(height_bytes)

        pixel_data = nparray_to_nya_bytes(image_data.pixels, image_data.width, image_data.height)

        f.write(pixel_data)

    return True