import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class NyaApp:
    def __init__(self):
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

        self.setup_home()

    def setup_home(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        options_frame = tk.Frame(self.root)
        options_frame.pack(expand=True)

        convert_to_button = tk.Button(options_frame, text="Convert to NYA file", command=self.setup_convert)
        convert_to_button.pack(pady=10)

        view_nya_button = tk.Button(options_frame, text="View NYA file")
        view_nya_button.pack(pady=10)

    def setup_convert(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
        back_button = tk.Button(self.root, text="Back", command=self.setup_home)
        back_button.place(x=10, y=10)

        select_frame = tk.Frame(self.root)
        select_frame.pack(expand=True)

        current_file = tk.StringVar(self.root, "No File Selected")

        def get_file():
            path = filedialog.askopenfilename(title="Select a file", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
            if path:
                current_file.set(path)

        select_file = tk.Button(select_frame, text="Select file", command=get_file)
        select_file.pack(pady=10)

        file_label = tk.Label(select_frame, textvariable=current_file)
        file_label.pack(pady=10)

        convert_button = tk.Button(select_frame, text="Convert")
        convert_button.pack(pady=10)

    def run(self):
        self.root.mainloop()