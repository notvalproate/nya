# NYA

**N**anological **Y**eildable **A**sset is a simple and clean file format that makes use of a **Run Length Encoding** + **Huffman Coding** algorithm applied on an selectively filtered image. **NYA** encodes using one of three filter types: *None*, *Difference* and *Up*. With a 9 byte header (4 magic bytes "NYA!" + 2 bytes width + 2 bytes height + 1 byte flags), **.nya** files support a maximum image size of **65,536 x 65,536** pixels in RGB (3-channel) or RGBA (4-channel, transparency).

## To Run The Converter
```
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python ./src/main.py
```
## To Open .nya Files
- Clone the repo: `git clone https://github.com/notvalproate/nya`

**Method 1:**
- Navigate to the repository in your preferred terminal: `cd nya`
- Run the executable followed by the filepath to the nya file: `nyaviewer.exe ./outputs/test.nya`

**Method 2:**
- Right click on any **.nya** file, and then click on `Properties`
- In the `Opens With:` option, select `Change`
- Navigate to the repository and select `nya.exe` as the application
- Click `Apply` and close the window
- Now simply double click on any **.nya** file to open it

## Build nyaviewer
**Prerequisites**
- SDL2 Installed. Get it from [here](https://github.com/libsdl-org/SDL/releases)
- GNU Compiler Collection ( >= GCC 8.0 )

**Steps**
- Switch to the viewer folder: `cd viewer`
- Edit the Makefile and replace `SDL_INCLUDE` and `SDL_LIB` with your paths
- Edit any other parameters to your liking
- Make the project: `make`
- Run and test the viewer: `./nyaviewer.exe ../outputs/icon.nya`
### Specification
Read the specification [here](https://github.com/user-attachments/files/17126200/NYA.IMAGE.FORMAT.SPECIFICATION.pdf)
