#include "Decoder.hpp"

#include <iostream>
#include <fstream>
#include <cstring>
#include <functional>
#include <iomanip>

void (*NYADecoder::NYAFunctions[4])(BitReader&, NYAImage*, NYA_QWord&) = {
    &decodeNYASingle,
    &decodeNYARun,
    &decodeNYAHuffmanSingle,
    &decodeNYAHuffmanRun
};
NYAHuffmanNode* NYADecoder::huffmanRoot = nullptr;
NYA_QWord NYADecoder::width = 0;
NYA_QWord NYADecoder::height = 0;
int NYADecoder::colorDepth = NYA_RGB;
int NYADecoder::filterType = 0;

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

    if (strncmp(reinterpret_cast<const char*>(&header.magic), "NYA!", 4) != 0) {
        std::cerr << "File specified is either corrupted or not a valid NYA file" << std::endl;
        return nullptr;
    }

    if (header.flags & NYA_FLAG_ALPHA) {
        colorDepth = NYA_RGBA;
    }
    filterType = header.flags & 0x03;
    width = header.width;
    height = header.height;

    BitReader reader(nyaFile);
    buildHuffmanTree(reader);

    NYAImage* image = new NYAImage();
    image->width = header.width;
    image->height = header.height;

    NYA_QWord pixelCount = static_cast<NYA_QWord>(header.width) * static_cast<NYA_QWord>(header.height);
    image->pixels = new NYA_DWord[pixelCount];

    NYA_QWord pixelIndex = 0;

    std::cout << "Decoding image..." << std::endl;

    while (pixelIndex < pixelCount) {
        auto tag = reader.readBits(2);
        std::cout << std::dec << tag << " " << pixelIndex << std::endl;
        NYAFunctions[tag](reader, image, pixelIndex);
    }

    std::cout << std::endl << "Image decoded" << std::endl;

    deleteHuffmanTree(huffmanRoot);
    return image;
}

void NYADecoder::decodeNYASingle(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex) {
    NYA_QWord value = readPixelValue(reader);
    image->pixels[transformIndex(pixelIndex)] = value;

    pixelIndex++;
}

void NYADecoder::decodeNYARun(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex) {
    NYA_QWord value = readPixelValue(reader);
    auto length = reader.readBits(3) + 1;
    auto run = reader.readBits(length) + 1;

    for (auto i = 0; i < run; i++) {
        image->pixels[transformIndex(pixelIndex)] = value;
        pixelIndex++;
    }
}

void NYADecoder::decodeNYAHuffmanSingle(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex) {
    NYA_QWord value = readHuffmanValue(reader);

    image->pixels[transformIndex(pixelIndex)] = value;

    pixelIndex++;
}

void NYADecoder::decodeNYAHuffmanRun(BitReader& reader, NYAImage* image, NYA_QWord& pixelIndex) {
    NYA_QWord value = readHuffmanValue(reader);
    auto length = reader.readBits(3) + 1;
    auto run = reader.readBits(length) + 1;

    for (auto i = 0; i < run; i++) {
        image->pixels[transformIndex(pixelIndex)] = value;
        pixelIndex++;
    }
}

void NYADecoder::buildHuffmanTree(BitReader& reader) {
    std::function<NYAHuffmanNode*(NYAHuffmanNode*)> getAncestorWithEmptyRight;

    getAncestorWithEmptyRight = [&](NYAHuffmanNode* node) {
        if (node == nullptr || node->right == nullptr) {
            return node;
        }

        return getAncestorWithEmptyRight(node->parent);
    };

    huffmanRoot = new NYAHuffmanNode();
    NYAHuffmanNode* currentNode = huffmanRoot;

    while (true) {
        NYA_Bit bit = reader.readBit();

        if (bit) {
            currentNode->value = readPixelValue(reader);
            currentNode = getAncestorWithEmptyRight(currentNode->parent);

            if (currentNode == nullptr) {
                break;
            }

            currentNode->right = new NYAHuffmanNode();
            currentNode->right->parent = currentNode;
            currentNode = currentNode->right;
        } else {
            currentNode->left = new NYAHuffmanNode();
            currentNode->left->parent = currentNode;
            currentNode = currentNode->left;
        }
    }
}

void NYADecoder::deleteHuffmanTree(NYAHuffmanNode* node) {
    if (node == nullptr) {
        return;
    }

    deleteHuffmanTree(node->left);
    deleteHuffmanTree(node->right);
    delete node;
}

NYA_QWord NYADecoder::readPixelValue(BitReader& reader) {
    NYA_QWord value = reader.readBits(colorDepth);

    if (colorDepth == NYA_RGB) {
        value = (value << 8) | 0xFF;
    }

    return value;
}

NYA_QWord NYADecoder::readHuffmanValue(BitReader& reader) {
    auto currentNode = huffmanRoot;

    while (currentNode->left != nullptr) {
        if (reader.readBit()) {
            currentNode = currentNode->right;
        } else {
            currentNode = currentNode->left;
        }
    }

    return currentNode->value;
}

NYA_DWord NYADecoder::transformIndex(NYA_DWord index) {
    if (filterType == 2) {
        return (width * (index % height)) + (index / height);
    }
    return index;
}