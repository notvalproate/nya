from numpy.typing import NDArray
from abc import ABC, abstractmethod
from typing import Tuple, Self

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
        self.ALPHA_ENCODING = False # ONE BIT
        self.DIFF_FILTER = False # ONE BIT
        self.HUFFMAN_CODED = False # ONE BIT
        self.WIDTH = 0 # 16 BITS
        self.HEIGHT = 0 # 16 BITS

    def to_bits(self) -> bitarray:
        bits = bitarray()
        bits.append(int(self.ALPHA_ENCODING))
        bits.append(int(self.DIFF_FILTER))
        bits.append(int(self.HUFFMAN_CODED))
        bits.frombytes(self.WIDTH.to_bytes(2, byteorder="big"))
        bits.frombytes(self.HEIGHT.to_bytes(2, byteorder="big"))
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
        count_length = adjusted_length.bit_length()
        length_length = count_length.bit_length()

        count_str = f'{adjusted_length:0{count_length}b}'
        length_str = f'{length_length:03b}'

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
        count_length = adjusted_length.bit_length()
        length_length = count_length.bit_length()

        count_str = f'{adjusted_length:0{count_length}b}'
        length_str = f'{length_length:03b}'

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

    previous = np.array([255, 255, 255, 255])

    if not header.ALPHA_ENCODING:
        pixels = pixels[:, :, :3]
        previous = np.array([255, 255, 255])

    ##################################################
    # STAGE 2: APPLY THE DIFFERENCE FILTER IF NEEDED #
    ##################################################

    # for row in pixels:
    #     i = 0
    #     while i < len(row):
    #         diff = row[i] - previous
    #         previous = row[i].copy()
    #         row[i] = diff
    #         i += 1
    
    #######################################################################################################################
    # STAGE 3: PERFORM RLE ENCODING AND STORE IT IN nya_pixels. nya_values WILL STORE THE COUNTS OF EACH DIFFERENCE/PIXEL #
    #######################################################################################################################

    # STAGE 3.1: FLATTEN PIXELS AND TREAT IT AS 1D ARRAY
    
    pixels = pixels.reshape(-1, pixels.shape[-1])

    # STAGE 3.2: PERFORM THE RLE ENCODING

    nya_pixels = []
    nya_frequency = defaultdict(int)
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
        nya_frequency[color_tuple] += 1

        ind += 1

    ############################################################################################################
    # STAGE 4: PERFORM HUFFMAN ENCODING ON THE MOST COMMON 256 DIFFERENCES WHILE SIMULTANEOUSLY SERIALIZING IT #
    ############################################################################################################

    nya_frequency = {key: value for key, value in nya_frequency.items() if value > 1}
    root = None
    serialized_tree = bitarray(endian="big")

    if len(nya_frequency) > 0:

        header.HUFFMAN_CODED = True

        # STAGE 4.1: ELIMINATE COLORS THAT APPEAR ONLY ONCE AND LIMIT TO 256 COLORS

        if len(nya_frequency) > 256:
            sorted_nya_frequency = sorted(nya_frequency.items(), key=lambda x: x[1], reverse=True)
            sorted_nya_frequency = dict(sorted_nya_frequency[:256])
            nya_frequency = sorted_nya_frequency
        
        # print("NYA DICT", len(nya_frequency))
        # for key, value in nya_frequency.items():
        #     print(f"{str(key).ljust(19)} : {value}")
            
        # STAGE 4.2: MAKE THE HEAP

        heap = []

        for key in nya_frequency:
            node = NYA_HUFFMAN_NODE(key, nya_frequency[key])
            heapq.heappush(heap, node)

        # STAGE 4.3: MAKE THE HUFFMAN TREE

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            parent = NYA_HUFFMAN_NODE(None, left.FREQUENCY + right.FREQUENCY)
            parent.LEFT = left
            parent.RIGHT = right

            heapq.heappush(heap, parent)

        # STAGE 4.4: MAKE THE HUFFMAN CODES

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

        # print("NYA HUFFMAN CODES")
        # for key, value in nya_huffman_codes.items():
        #     print(f"{str(key).ljust(19)} : {value}")

        # STAGE 4.5: APPLY/USE THE HUFFMAN CODES BY REPLACING BLOCKS

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

    #############################
    # STAGE 5: RETURN THE BYTES #
    #############################

    nya_data = bitarray(endian="big")

    # STAGE 5.1: ADD HEADER

    nya_data.extend(header.to_bits())

    # STAGE 5.2: ADD HUFFMAN TREE IF NEEDED

    if root != None:
        nya_data.extend(serialized_tree)

    # STAGE 5.3: ADD PIXELS

    for block in nya_pixels:
        nya_data.extend(block.to_bits())

    import math
    print(f'Converted to {math.ceil(len(nya_data) / 8.0)} Bytes')

    return nya_data.tobytes()

    
def convert_to_nya(image_path: str, output_dir: str) -> bool:
    img = Image.open(image_path)
    width, height = img.size
    img = img.convert("RGBA")
    pixels = np.array(img)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        nya_data = nparray_to_nya_bytes(pixels, width, height)
        f.write(nya_data)

    return True