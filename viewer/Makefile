CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Wpedantic -IC:\dev\libraries\SDL2\dev\SDL2-2.30.7\x86_64-w64-mingw32\include
LDFLAGS = -LC:\dev\libraries\SDL2\dev\SDL2-2.30.7\x86_64-w64-mingw32\lib -lmingw32 -lSDL2main -lSDL2

SRC_DIR = src
BUILD_DIR = build

SRC_FILES = $(wildcard $(SRC_DIR)/*.cpp)
OBJ_FILES = $(patsubst $(SRC_DIR)/%.cpp, $(BUILD_DIR)/%.o, $(SRC_FILES))

OUTPUT = nyaviewer

all: $(OUTPUT)

$(OUTPUT): $(OBJ_FILES)
	$(CXX) $(OBJ_FILES) -o $(OUTPUT) $(LDFLAGS)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
