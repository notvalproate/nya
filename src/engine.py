from numpy.typing import NDArray
from abc import ABC, abstractmethod
from typing import Tuple, Self, List

from PIL import Image
import numpy as np
from bitarray import bitarray

import os
from collections import defaultdict
import heapq


class NYA_BLOCK(ABC):
    @abstractmethod
    def to_bits(self) -> bitarray:
        pass


class NYA_HEADER(NYA_BLOCK):
    def __init__(self):
        self.MAGIC = "NYA!"

        self.WIDTH = 0 # 16 BITS
        self.HEIGHT = 0 # 16 BITS

        self.PADDING = bitarray([0, 0, 0, 0, 0])
        self.ALPHA_ENCODING = False # ONE BIT
        self.FILTER = 0 # TWO BITS

    def to_bits(self) -> bitarray:
        bits = bitarray()

        for char in self.MAGIC:
            bits.extend([int(bit) for bit in f'{ord(char):08b}'])

        bits.frombytes(self.WIDTH.to_bytes(2, byteorder="little"))
        bits.frombytes(self.HEIGHT.to_bytes(2, byteorder="little"))

        bits.extend(self.PADDING)
        bits.append(int(self.ALPHA_ENCODING))
        bits.extend(int(bit) for bit in f'{self.FILTER:02b}')

        return bits


class NYA_SINGLE(NYA_BLOCK):
    tag = bitarray([0, 0])

    def __init__(self, value: NDArray[np.uint8]):
        self.VALUE = value

    def to_bits(self) -> bitarray:
        bits = self.tag.copy()
        bits.frombytes(self.VALUE.tobytes())
        return bits


class NYA_RUN(NYA_SINGLE):
    tag = bitarray([0, 1])

    def __init__(self, value: NDArray[np.uint8], length: int):
        super().__init__(value)
        self.LENGTH = length

    def to_bits(self) -> bitarray:
        adjusted_length = self.LENGTH - 1
        count_length = adjusted_length.bit_length() - 1

        length_str = f'{count_length:03b}'
        count_str = f'{adjusted_length:0{count_length}b}'

        bits = self.tag.copy()
        bits.frombytes(self.VALUE.tobytes())
        bits.extend([int(bit) for bit in length_str])
        bits.extend([int(bit) for bit in count_str])

        return bits


class NYA_SINGLE_HUFFMAN(NYA_BLOCK):
    tag = bitarray([1, 0])

    def __init__(self, code: bitarray):
        self.CODE = code

    def to_bits(self) -> bitarray:
        bits = self.tag.copy()
        bits.extend(self.CODE)
        return bits


class NYA_RUN_HUFFMAN(NYA_SINGLE_HUFFMAN):
    tag = bitarray([1, 1])

    def __init__(self, code: bitarray, length: int):
        super().__init__(code)
        self.LENGTH = length

    def to_bits(self) -> bitarray:
        adjusted_length = self.LENGTH - 1
        count_length = adjusted_length.bit_length() - 1

        length_str = f'{count_length:03b}'
        count_str = f'{adjusted_length:0{count_length}b}'

        bits = self.tag.copy()
        bits.extend(self.CODE)
        bits.extend([int(bit) for bit in length_str])
        bits.extend([int(bit) for bit in count_str])

        return bits
    

class NYA_HUFFMAN_NODE:
    def __init__(self, value: Tuple[int, int, int] | None, frequency: int):
        self.VALUE = value
        self.FREQUENCY = frequency
        self.LEFT = None
        self.RIGHT = None

    def __lt__(self, other: Self):
        return self.FREQUENCY < other.FREQUENCY
    
    def __eq__(self, other: Self):
        if other == None:
            return False
        
        if not isinstance(other, NYA_HUFFMAN_NODE):
            return False
        
        return self.FREQUENCY == other.FREQUENCY
    

def rle_encode_pixels(pixels: np.array) -> Tuple[List[NYA_SINGLE | NYA_RUN], defaultdict]:
    nya_pixels = []
    nya_frequencies = defaultdict(int)
    ind = 0
    pixel_count = len(pixels)

    while ind < pixel_count:
        curr_pixel = pixels[ind]
        length = 1

        while ind + length < pixel_count and length <= 256 and np.array_equal(curr_pixel, pixels[ind + length]):
            length += 1

        if length == 1:
            nya_pixels.append(NYA_SINGLE(curr_pixel))
        else:
            nya_pixels.append(NYA_RUN(curr_pixel, length))
            ind += length - 1

        color_tuple = tuple(int(x) for x in curr_pixel)
        nya_frequencies[color_tuple] += 1

        ind += 1

    nya_frequencies = {key: value for key, value in nya_frequencies.items() if value > 1}

    return nya_pixels, nya_frequencies


def huffman_code_pixels(nya_pixels: List[NYA_SINGLE | NYA_RUN], nya_frequencies: defaultdict) -> bitarray:
    root = None
    serialized_tree = bitarray(endian="big")
  
    if len(nya_frequencies) > 256:
        sorted_nya_frequency = sorted(nya_frequencies.items(), key=lambda x: x[1], reverse=True)
        sorted_nya_frequency = dict(sorted_nya_frequency[:256])
        nya_frequencies = sorted_nya_frequency

    heap = []

    for key in nya_frequencies:
        node = NYA_HUFFMAN_NODE(key, nya_frequencies[key])
        heapq.heappush(heap, node)

    if len(nya_frequencies) == 1:
        for key in nya_frequencies:
            node = NYA_HUFFMAN_NODE(key, nya_frequencies[key])
            heapq.heappush(heap, node)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        parent = NYA_HUFFMAN_NODE(None, left.FREQUENCY + right.FREQUENCY)
        parent.LEFT = left
        parent.RIGHT = right

        heapq.heappush(heap, parent)

    nya_huffman_codes = {}
    root = heapq.heappop(heap)

    def make_huffman_codes(node: NYA_HUFFMAN_NODE, current_code: bitarray):
        if node == None:
            return

        if node.VALUE != None:
            serialized_tree.append(1)
            for channel in node.VALUE:
                serialized_tree.extend(format(channel, '08b'))

            nya_huffman_codes[node.VALUE] = current_code.copy()
            return
        
        serialized_tree.append(0)
        make_huffman_codes(node.LEFT, current_code + bitarray([0]))
        make_huffman_codes(node.RIGHT, current_code + bitarray([1]))

    make_huffman_codes(root, bitarray())

    ind = 0

    while ind < len(nya_pixels):
        color_tuple = tuple(int(x) for x in nya_pixels[ind].VALUE)

        if color_tuple in nya_huffman_codes:
            code = nya_huffman_codes[color_tuple]

            if isinstance(nya_pixels[ind], NYA_RUN):
                nya_pixels[ind] = NYA_RUN_HUFFMAN(code, nya_pixels[ind].LENGTH)
            else:
                nya_pixels[ind] = NYA_SINGLE_HUFFMAN(code)

        ind += 1

    return serialized_tree


def encode_nya(pixels: np.array) -> Tuple[bitarray, bool]:
    encoded = bitarray(endian="big")
    is_huffman_coded = False
    pixels = pixels.reshape(-1, pixels.shape[-1])

    nya_pixels, nya_frequencies = rle_encode_pixels(pixels)

    serialized_tree = huffman_code_pixels(nya_pixels, nya_frequencies)
    encoded.extend(serialized_tree)
    is_huffman_coded = True

    for block in nya_pixels:
        encoded.extend(block.to_bits())

    return encoded, is_huffman_coded


def none_encode_nya(src_pixels: np.array) -> Tuple[bitarray, bool]:
    pixels = src_pixels.copy()
    return encode_nya(pixels)


def diff_encode_nya(src_pixels: np.array, alpha_encoded: bool) -> Tuple[bitarray, bool]:
    pixels = src_pixels.copy()
    previous = np.zeros(4, dtype=np.uint8) if alpha_encoded else np.array([255, 255, 255], dtype=np.uint8)

    for row in pixels:
        i = 0
        while i < len(row):
            diff = row[i] - previous
            previous = row[i].copy()
            row[i] = diff
            i += 1

    return encode_nya(pixels)


def up_encode_nya(src_pixels: np.array, alpha_encoded: bool) -> Tuple[bitarray, bool]:
    pixels = src_pixels.copy()
    previous = np.zeros(4, dtype=np.uint8) if alpha_encoded else np.array([255, 255, 255], dtype=np.uint8)

    pixels = np.swapaxes(pixels, 0, 1)

    for row in pixels:
        i = 0
        while i < len(row):
            diff = row[i] - previous
            previous = row[i].copy()
            row[i] = diff
            i += 1

    pixels = np.swapaxes(pixels, 0, 1)

    return encode_nya(pixels)


def get_bytes_string(bit_count: int) -> str:
    import math
    byte_size = math.ceil(bit_count / 8.0)
    return f'{byte_size} Bytes | {byte_size / 1024} KB'


def nparray_to_nya_bytes(pixels: np.array, width: int, height: int) -> bytes:

    ################################################################
    # STAGE 0: CREATE EMPTY HEADER WHICH WILL BE MODIFIED AS WE GO #
    ################################################################

    header = NYA_HEADER()
    header.WIDTH = width
    header.HEIGHT = height

    ###########################################
    # STAGE 1: DECIDE BETWEEN 3 OR 4 CHANNELS #
    ###########################################

    for row in pixels:
        for pixel in row:
            if pixel[3] != 255:
                header.ALPHA_ENCODING = True
                break

    if not header.ALPHA_ENCODING:
        pixels = pixels[:, :, :3]

    ##############################################################
    # STAGE 2: COMPRESS USING DIFFERENT FILTERS AND USE BEST ONE #
    ##############################################################

    # STAGE 2.1: FILTER 0 - NO FILTER
    none_data, none_is_huffman = none_encode_nya(pixels)

    # STAGE 2.2: FILTER 1 - DIFF
    diff_data, diff_is_huffman = diff_encode_nya(pixels, header.ALPHA_ENCODING)

    # STAGE 2.3: FILTER 2 - UP
    up_data, up_is_huffman = up_encode_nya(pixels, header.ALPHA_ENCODING)

    # STAGE 2.4: TAKE MINIMUM OF FILTER 0, 1, 2

    print(f'NONE: {get_bytes_string(len(none_data))} \nDIFF: {get_bytes_string(len(diff_data))} \nUP: {get_bytes_string(len(up_data))}')

    final_data = none_data
    header.HUFFMAN_CODED = none_is_huffman

    if len(diff_data) < len(final_data):
        final_data = diff_data
        header.FILTER = 1
        header.HUFFMAN_CODED = diff_is_huffman

    if len(up_data) < len(final_data):
        final_data = up_data
        header.FILTER = 2
        header.HUFFMAN_CODED = up_is_huffman

    #############################
    # STAGE 3: RETURN THE BYTES #
    #############################
    nya_data = bitarray(endian="big")

    # STAGE 3.1: ADD HEADER
    nya_data.extend(header.to_bits())

    # STAGE 3.2: ADD PIXELS
    nya_data.extend(final_data)

    # STAGE 3.3: ADD PADDING
    padding = 8 - (len(nya_data) % 8)
    nya_data.extend([0] * padding)

    # STAGE 3.4: ADD BYTE STREAM END "0x00 0x00 : 3"
    nya_data.extend([0] * 16)
    for char in ':3':
        nya_data.extend([int(bit) for bit in f'{ord(char):08b}'])

    print(f'FINAL SIZE: {get_bytes_string(len(nya_data))}')

    return nya_data.tobytes()
    
def convert_to_nya(image_path: str, output_dir: str) -> bool:
    img = Image.open(image_path)
    width, height = img.size
    img = img.convert("RGBA")
    pixels = np.array(img)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        print(f'COMPRESSING TO FILE: {output_file}')
        nya_data = nparray_to_nya_bytes(pixels, width, height)
        f.write(nya_data)

    return True