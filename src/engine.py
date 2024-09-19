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
    def to_bits(self) -> bitarray:
        pass


class NYA_SINGLE(NYA_BLOCK):
    tag = bitarray([0])

    def __init__(self, value: NDArray[np.uint8]):
        self.VALUE = value

    def to_bits(self) -> bitarray:
        bits = self.tag.copy()
        bits.frombytes(self.VALUE.tobytes())
        return bits


class NYA_RUN(NYA_SINGLE):
    tag = bitarray([1])

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
        length_str = f'{self.LENGTH-1:06b}'
        bits = self.tag.copy()
        bits.extend(self.CODE)
        bits.extend([int(bit) for bit in length_str])
        return bits


def nparray_to_nya_bytes(pixels: np.array, width: int) -> bytes:

    ################################################################
    # STAGE 0: CREATE EMPTY HEADER WHICH WILL BE MODIFIED AS WE GO #
    ################################################################

    header = NYA_HEADER()
    header.WIDTH = width

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

    ########################################
    # STAGE 2: APPLY THE DIFFERENCE FILTER #
    ########################################

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
    nya_values = {}
    ind = 0
    pixel_count = len(pixels)

    single_run_count = 0
    run_run_count = 0

    while ind < pixel_count:
        curr_pixel = pixels[ind]
        length = 1

        while ind + length < pixel_count and length <= 256 and np.array_equal(curr_pixel, pixels[ind + length]):
            length += 1

        if length == 1:
            nya_pixels.append(NYA_SINGLE(curr_pixel))
            single_run_count += 1
        else:
            nya_pixels.append(NYA_RUN(curr_pixel, length))
            ind += length - 1
            run_run_count += 1

        if tuple(pixels[ind]) in nya_values:
            nya_values[tuple(pixel)] += 1
        else:
            nya_values[tuple(pixel)] = 1

        ind += 1

    ########################################################################
    # STAGE 4: PERFORM HUFFMAN ENCODING ON THE MOST COMMON 256 DIFFERENCES #
    ########################################################################

    #####################################################################
    # STAGE 5: WRITE EVERYTHING TO A BITARRAY AND THEN RETURN THE BYTES #
    #####################################################################

    #############################
    # STAGE 6: RETURN THE BYTES #
    #############################

    nya_data = bitarray(endian="big")

    # STAGE 6.1: ADD HEADER
    nya_data.append(int(header.ALPHA_ENCODING))
    nya_data.append(int(header.VERTICAL_ENCODING))
    nya_data.frombytes(header.WIDTH.to_bytes(2, byteorder="big"))

    # STAGE 6.2: ADD PIXELS
    for block in nya_pixels:
        nya_data.extend(block.to_bits())

    print(f"Single Run Count: {single_run_count}, Run Run Count: {run_run_count}")

    return nya_data.tobytes()
    
def convert_to_nya(image_path: str, output_dir: str) -> bool:
    img = Image.open(image_path)
    width, height = img.size
    img = img.convert("RGBA")
    pixels = np.array(img)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        nya_data = nparray_to_nya_bytes(pixels, width)
        f.write(nya_data)

    return True