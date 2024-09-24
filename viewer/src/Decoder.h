#include <filesystem>

struct NYAImage {
    uint32_t width;
    uint32_t height;
    uint32_t* pixels;

    ~NYAImage() {
        delete[] pixels;
    }
};

struct NYAHuffmanNode {
    uint32_t value;
    NYAHuffmanNode* left;
    NYAHuffmanNode* right;
    NYAHuffmanNode* parent;
};

class NYADecoder {
public:
    static NYAImage* decodeFromPath(const std::filesystem::path& path);
};