#include <filesystem>
#include <fstream>

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
    NYA_Word width;
    NYA_Word height;
    NYA_DWord* pixels;

    ~NYAImage() {
        delete[] pixels;
    }
};

struct NYAHuffmanNode {
    NYA_DWord value;
    NYAHuffmanNode* left;
    NYAHuffmanNode* right;
    NYAHuffmanNode* parent;
};

#include "BitReader.hpp"

class NYADecoder {
public:
    static NYAImage* decodeFromPath(const std::filesystem::path& path);
private:
    static void buildHuffmanTree(BitReader& reader);
    static NYAHuffmanNode* huffmanRoot;
};