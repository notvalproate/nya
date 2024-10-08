#include <filesystem>
#include <fstream>

#define NYA_MAGIC "NYA!"
#define NYA_MAGIC_LENGTH 4

#define NYA_FLAG_ALPHA 0x04
#define NYA_FILTER_MASK 0x03

#define NYA_FILTER_NONE 0
#define NYA_FILTER_SUB 1
#define NYA_FILTER_UP 2

#define NYA_RGB 24
#define NYA_RGBA 32

#define NYA_PREVIOUS_RGB 0xFFFFFFFF
#define NYA_PREVIOUS_RGBA 0x00000000
#define NYA_SHIFT_R 24
#define NYA_SHIFT_G 16
#define NYA_SHIFT_B 8
#define NYA_RGB_MASK 0xFFFFFF00
#define NYA_BYTE_MASK 0xFF

#define NYA_BLOCK_TYPE_COUNT 4
#define NYA_TAG_LENGTH 2
#define NYA_LENGTH_BITCOUNT 3

typedef bool NYA_Bit;
typedef uint8_t NYA_Byte;
typedef uint16_t NYA_Word;
typedef uint32_t NYA_DWord;

struct NYAHeader {
    NYA_Byte magic[NYA_MAGIC_LENGTH];
    NYA_Word width;
    NYA_Word height;
    NYA_Byte flags;

    NYAHeader(std::ifstream& file) {
        file.read(reinterpret_cast<char*>(&magic), NYA_MAGIC_LENGTH);
        file.read(reinterpret_cast<char*>(&width), sizeof(NYA_Word));
        file.read(reinterpret_cast<char*>(&height), sizeof(NYA_Word));
        file.read(reinterpret_cast<char*>(&flags), sizeof(NYA_Byte));
    }
};

struct NYAImage {
    NYA_Word width = 0;
    NYA_Word height = 0;
    NYA_DWord* pixels = nullptr;

    ~NYAImage() {
        delete[] pixels;
    }
};

struct NYAHuffmanNode {
    NYA_DWord value = 0;
    NYAHuffmanNode* left = nullptr;
    NYAHuffmanNode* right = nullptr;
    NYAHuffmanNode* parent = nullptr; 
};

#include "BitReader.hpp"

class NYADecoder {
public:
    static NYAImage* decodeFromPath(const std::filesystem::path& path);
private:
    static void decodeNYASingle(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex);
    static void decodeNYARun(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex);
    static void decodeNYAHuffmanSingle(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex);
    static void decodeNYAHuffmanRun(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex);

    static void buildHuffmanTree(BitReader& reader);
    static void deleteHuffmanTree(NYAHuffmanNode* node);

    static NYA_DWord readPixelValue(BitReader& reader);
    static NYA_DWord readHuffmanValue(BitReader& reader);
    static NYA_DWord transformIndex(NYA_DWord index);

    static void applyFilter(NYAImage* image, NYA_DWord pixelCount);

    static NYAHuffmanNode* huffmanRoot;
    static int colorDepth;
    static int filterType;
    static NYA_Word width, height;
    static NYA_DWord previousValue;
    static void (*NYAFunctions[NYA_BLOCK_TYPE_COUNT])(BitReader&, NYAImage*, NYA_DWord&);
};