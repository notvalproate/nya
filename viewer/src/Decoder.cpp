#include "Decoder.h"
#include <iostream>
#include <fstream>
#include <cstring>

NYAHuffmanNode* NYADecoder::huffmanRoot = nullptr;

NYAImage* NYADecoder::decodeFromPath(const std::filesystem::path& path) {
    if (path.extension() != ".nya") {
        std::cerr << "File specified is not a .nya file" << std::endl;
        return nullptr;
    }

    std::ifstream nyaFile(path.c_str(), std::ios::binary);

    if (!nyaFile.is_open()) {
        std::cerr << "Failed to open specified file" << std::endl;
        return nullptr;
    }

    NYAHeader header(nyaFile);

    if (strncmp(header.magic, "NYA!", 4) != 0) {
        std::cerr << "File specified is either corrupted or not a valid NYA file" << std::endl;
        return nullptr;
    }

    buildHuffmanTree(nyaFile);

    NYAImage* image = new NYAImage();
    image->width = header.width;
    image->height = header.height;
    image->pixels = new NYA_DWord[static_cast<NYA_QWord>(header.width) * static_cast<NYA_QWord>(header.height)];

    return image;
}

void NYADecoder::buildHuffmanTree(std::ifstream& file) {
    
}