import tkinter as tk
import os
from tkinter import filedialog
from PIL import Image, ImageTk
import engine

class NyaApp:
    root = tk.Tk
    current_file = tk.StringVar
    output_dir = tk.StringVar
    view_file = tk.StringVar

    def __init__(self):
        # Initialize the Tkinter window
        self.root = tk.Tk()
        self.root.title("nya")

        window_height = 300
        window_width = 450
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.resizable(False, False)
        ico = Image.open("assets/icon.png")
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)

        # Some global variables
        
        self.current_file = tk.StringVar(self.root, "No File Selected")
        self.output_dir = tk.StringVar(self.root, os.getcwd() + os.sep + "outputs")

        self.setup_convert()

    def setup_convert(self) -> None:
        select_frame = tk.Frame(self.root)
        select_frame.pack(expand=True)

        def get_file():
            path = filedialog.askopenfilename(title="Select a file", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
            if path:
                self.current_file.set(os.path.normpath(path))

        def get_dir():
            path = filedialog.askdirectory(title="Select a directory")
            if path:
                self.output_dir.set(os.path.normpath(path))

        select_file = tk.Button(select_frame, text="Select file", command=get_file)
        select_file.pack(pady=10)

        file_label = tk.Label(select_frame, textvariable=self.current_file)
        file_label.pack(pady=10)

        select_dir = tk.Button(select_frame, text="Select Output Directory", command=get_dir)
        select_dir.pack(pady=10)

        dir_label = tk.Label(select_frame, textvariable=self.output_dir)
        dir_label.pack(pady=10)

        convert_button = tk.Button(select_frame, text="Convert", command=lambda: engine.convert_to_nya(self.current_file.get(), self.output_dir.get()))
        convert_button.pack(pady=10)

    def run(self) -> None:
        self.root.mainloop()