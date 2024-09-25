#include <filesystem>
#include <fstream>

#define NYA_MAGIC "NYA!"
#define NYA_FLAG_ALPHA 0x04
#define NYA_RGB 24
#define NYA_RGBA 32

typedef bool NYA_Bit;
typedef uint8_t NYA_Byte;
typedef uint16_t NYA_Word;
typedef uint32_t NYA_DWord;
typedef uint64_t NYA_QWord;

struct NYAHeader {
    NYA_Byte magic[4];
    NYA_Word width;
    NYA_Word height;
    NYA_Byte flags;

    NYAHeader(std::ifstream& file) {
        file.read(reinterpret_cast<char*>(&magic), 4);
        file.read(reinterpret_cast<char*>(&width), 2);
        file.read(reinterpret_cast<char*>(&height), 2);
        file.read(reinterpret_cast<char*>(&flags), 1);
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
    static void decodeNYASingle(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex);
    static void decodeNYARun(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex);
    static void decodeNYAHuffmanSingle(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex);
    static void decodeNYAHuffmanRun(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex);

    static void buildHuffmanTree(BitReader& reader);
    static void deleteHuffmanTree(NYAHuffmanNode* node);

    static NYA_QWord readPixelValue(BitReader& reader);
    static NYA_QWord readHuffmanValue(BitReader& reader);
    static NYA_DWord transformIndex(NYA_DWord index);

    static NYAHuffmanNode* huffmanRoot;
    static int colorDepth;
    static int filterType;
    static NYA_QWord width, height;
    static void (*NYAFunctions[4])(BitReader&, NYAImage*, NYA_QWord&);
};