from PIL import Image
import numpy as np

class ImageData:
    width = int
    height = int
    pixels = np.array

    def init(self, path):
        img = Image.open(path)
        self.width, self.height = img.size
        img = img.convert("RGBA")
        self.pixels = np.array(img)

def convert_to_nya(image_path: str, output_dir: str) -> None:
    image_data = ImageData(image_path)
    print(image_data.pixels)
