import sys
import matplotlib.pyplot as plt
import numpy as np

def nya_bytes_to_nparray(nya_bytes: bytes, width: int, height: int) -> np.array:
    return np.frombuffer(nya_bytes, dtype=np.uint8).reshape((height, width, 4))

def display_image_pixels(pixels: np.array, path: str) -> None:
    plt.gcf().canvas.manager.set_window_title(path)
    plt.imshow(pixels)
    plt.axis('off')
    plt.show()

def display_nya_file(nya_file: str) -> None:
    with open(nya_file, "rb") as f:
        width = int.from_bytes(f.read(16), byteorder="big")
        height = int.from_bytes(f.read(16), byteorder="big")

        pixel_data = f.read()
        pixels = nya_bytes_to_nparray(pixel_data, width, height)

        display_image_pixels(pixels, nya_file)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: myapp.exe <file_path>")
        sys.exit(1)

    filepath = sys.argv[1]
    display_nya_file(filepath)