from numpy.typing import NDArray
from abc import ABC, abstractmethod

from PIL import Image
import numpy as np
import os
from bitarray import bitarray


class NYA_HEADER:
    def __init__(self):
        self.ALPHA_ENCODING = False # ONE BIT
        self.VERTICAL_ENCODING = False # ONE BIT
        self.WIDTH = 0 # 16 BITS


class NYA_BLOCK(ABC):
    @abstractmethod
    def to_bytes(self) -> bytes:
        pass


class NYA_SINGLE(NYA_BLOCK):
    tag = bitarray([0, 0])

    def __init__(self, value: NDArray[np.uint8]):
        self.VALUE = value

    def to_bytes(self) -> bytes:
        return self.tag.frombytes(self.VALUE.tobytes())


class NYA_RUN(NYA_SINGLE):
    tag = bitarray([0, 1])

    def __init__(self, value: NDArray[np.uint8], length: int):
        super().__init__(value)
        self.LENGTH = length

    def to_bytes(self) -> bytes:
        length_str = f'{self.LENGTH-1:06b}'
        return self.tag.frombytes(self.VALUE.tobytes()).extend([int(bit) for bit in length_str])


class NYA_SINGLE_HUFFMAN(NYA_BLOCK):
    tag = bitarray([1, 0])

    def __init__(self, code: bitarray):
        self.CODE = code

    def to_bytes(self) -> bytes:
        return self.tag.extend(self.CODE)


class NYA_RUN_HUFFMAN(NYA_SINGLE_HUFFMAN):
    tag = bitarray([1, 1])

    def __init__(self, code: bitarray, length: int):
        super().__init__(code)
        self.LENGTH = length

    def to_bytes(self) -> bytes:
        length_str = f'{self.LENGTH-1:06b}'
        return self.tag.extend(self.CODE).extend([int(bit) for bit in length_str])


def nparray_to_nya_bytes(pixels: np.array, width: int) -> bytes:
    # STAGE 0: CREATE EMPTY HEADER WHICH WILL BE MODIFIED AS WE GO 
    header = NYA_HEADER()
    header.WIDTH = width

    # STAGE 1: DECIDE BETWEEN 3 OR 4 CHANNELS

    for row in pixels:
        for pixel in row:
            if pixel[3] != 255:
                header.ALPHA_ENCODING = True
                break

    previous = np.array([255, 255, 255, 255])

    if not header.ALPHA_ENCODING:
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
    
    # STAGE 3.1: FLATTEN PIXELS AND TREAT IT AS 1D ARRAY
    
    pixels = pixels.reshape(-1, pixels.shape[-1])

    # STAGE 3: PERFORM RLE ENCODING AND STORE IT IN nya_pixels. nya_values WILL STORE THE COUNTS OF EACH DIFFERENCE/PIXEL

    nya_pixels = []
    nya_values = {}
    ind = 0
    pixel_count = len(pixels)

    while ind < pixel_count:
        curr_pixel = pixels[ind]
        length = 1

        while ind + length < pixel_count and length <= 64 and np.array_equal(curr_pixel, pixels[ind + length]):
            length += 1

        if tuple(pixels[ind]) in nya_values:
            nya_values[tuple(pixel)] += 1
        else:
            nya_values[tuple(pixel)] = 1


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
    img = Image.open(image_path)
    width, height = img.size
    img = img.convert("RGBA")
    pixels = np.array(img)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        width_bytes = width.to_bytes(16, byteorder="big")
        height_bytes = height.to_bytes(16, byteorder="big")

        f.write(width_bytes)
        f.write(height_bytes)

        pixel_data = nparray_to_nya_bytes(pixels, width)

        f.write(pixel_data)

    return True