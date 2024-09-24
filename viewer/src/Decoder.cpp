#include "Decoder.hpp"

#include <iostream>
#include <fstream>
#include <cstring>
#include <functional>
#include <iomanip>

NYAHuffmanNode* NYADecoder::huffmanRoot = nullptr;
int NYADecoder::colorDepth = NYA_RGB;

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

    BitReader reader(nyaFile);
    buildHuffmanTree(reader);

    NYAImage* image = new NYAImage();
    image->width = header.width;
    image->height = header.height;
    image->pixels = new NYA_DWord[static_cast<NYA_QWord>(header.width) * static_cast<NYA_QWord>(header.height)];

    std::cout << "Decoding image..." << std::endl;

    deleteHuffmanTree(huffmanRoot);
    return image;
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
            currentNode->value = reader.readBits(colorDepth);

            if (colorDepth == NYA_RGB) {
                currentNode->value = (currentNode->value << 8) | 0xFF;
            }

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