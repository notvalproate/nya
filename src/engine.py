from PIL import Image
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

def convert_to_nya(image_path: str, output_dir: str) -> None:
    image_data = ImageData(image_path)


    file_name = image_path.split(os.sep)[-1].split(".")[0]
    output_file = f'{output_dir}{os.sep}{file_name}.nya'

    with open(output_file, "wb") as f:
        width_bytes = image_data.width.to_bytes(16, byteorder="big")
        height_bytes = image_data.height.to_bytes(16, byteorder="big")

        f.write(width_bytes)
        f.write(height_bytes)

        pixels_flat = image_data.pixels.flatten()
        pixel_data = pixels_flat.astype(np.int8).tobytes()

        f.write(pixel_data)