# NYA
![icon](https://github.com/user-attachments/assets/8b9afcc3-1040-4a17-bf58-0b6d670fb386)

**N**anological **Y**eildable **A**sset is a simple and clean lossless image file format that makes use of a **Run Length Encoding** + **Huffman Coding** algorithm applied on a selectively filtered image. **NYA** encodes using one of three filter types: *None*, *Difference* and *Up*. With a 9 byte header (4 magic bytes "NYA!" + 2 bytes width + 2 bytes height + 1 byte flags), **.nya** files support a maximum image size of **65,536 x 65,536** pixels in RGB (3-channel) or RGBA (4-channel, transparency).

## To Run The Converter
```
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python ./src/main.py
```
## To Open .nya Files
- Get the latest release from https://github.com/notvalproate/nya/releases

**Method 1:**
- Navigate to the folder in your preferred terminal: `cd nya`
- Run the executable followed by the filepath to the nya file: `nyaviewer.exe C:/dev/outputs/test.nya`

**Method 2:**
- Right click on any **.nya** file, and then click on `Properties`
- In the `Opens With:` option, select `Change`
- Navigate to the repository and select `nyaviewer.exe` as the application
- Click `Apply` and close the window
- Now simply double click on any **.nya** file to open it

## Build nyaviewer
**Prerequisites**
- SDL2 Installed. Get it from [here](https://github.com/libsdl-org/SDL/releases)
- GNU Compiler Collection ( >= GCC 8.0 )
- CMake ( >= CMake 3.0 )

**Steps**
- Switch to the viewer folder: `cd viewer`
- Create a build folder: `mkdir build`
- Go into the build folder: `cd build`
- Move into it and run cmake: `cmake ..`
- Make the project: `make`
- Place your `SDL2.dll` in the folder with the executable
- Go back to viewer folder: `cd ..`
- Run and test the viewer: `./nyaviewer.exe ../outputs/icon.nya`

## Install nyaviewer
**Prerequisites**
- Same as Build prerequisites

**Steps**
- Switch to the viewer folder: `cd viewer`
- Create a build folder: `mkdir build`
- Go into the build folder: `cd build`
- Move into it and run cmake: `cmake ..`
- Install nyaviewer: `make install`

**NOTE:** nyaviewer will be installed to your default install path. On windows you will still have to copy the SDL2.dll to the installed nyaviewer folder for the program to run.

### Specification
Read the specification [here](https://github.com/user-attachments/files/17126200/NYA.IMAGE.FORMAT.SPECIFICATION.pdf)
