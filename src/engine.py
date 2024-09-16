from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

class ImageData:
    width = int
    height = int
    pixels = np.array

    def __init__(self, path):
        img = Image.open(path)
        self.width, self.height = img.size
        img = img.convert("RGBA")
        self.pixels = np.array(img)

# a compression/encoding algorithm that compresses the data in some way or the other
def nparray_to_nya_bytes(pixels: np.array, width: int, height: int) -> bytes:
    pixels_flat = pixels.flatten()
    pixel_data = pixels_flat.astype(np.uint8).tobytes()
    return pixel_data

# a decompression/decoding algorithm that decompresses the data in some way or the other
def nya_bytes_to_nparray(nya_bytes: bytes, width: int, height: int) -> np.array:
    return np.frombuffer(nya_bytes, dtype=np.uint8).reshape((height, width, 4))

def display_image_pixels(pixels: np.array) -> None:
    plt.imshow(pixels)
    plt.axis('off')
    plt.show()
    
def convert_to_nya(image_path: str, output_dir: str) -> None:
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

def display_nya_file(nya_file: str) -> None:
    with open(nya_file, "rb") as f:
        width = int.from_bytes(f.read(16), byteorder="big")
        height = int.from_bytes(f.read(16), byteorder="big")

        pixel_data = f.read()
        pixels = nya_bytes_to_nparray(pixel_data, width, height)

        display_image_pixels(pixels)