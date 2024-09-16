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

def display_image_pixels(pixels: np.array) -> None:
    plt.imshow(pixels)
    plt.axis('off')
    plt.show()
    
def convert_to_nya(image_path: str, output_dir: str) -> None:
    image_data = ImageData(image_path)

    # Display image for testing
    display_image_pixels(image_data.pixels)

    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        width_bytes = image_data.width.to_bytes(16, byteorder="big")
        height_bytes = image_data.height.to_bytes(16, byteorder="big")

        f.write(width_bytes)
        f.write(height_bytes)

        pixels_flat = image_data.pixels.flatten()
        pixel_data = pixels_flat.astype(np.uint8).tobytes()

        f.write(pixel_data)

def display_nya_file(nya_file: str) -> None:
    with open(nya_file, "rb") as f:
        width = int.from_bytes(f.read(16), byteorder="big")
        height = int.from_bytes(f.read(16), byteorder="big")

        pixel_data = f.read()
        pixels = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width, 4))

        display_image_pixels(pixels)