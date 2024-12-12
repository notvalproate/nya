#include "Decoder.hpp"

#include <iostream>
#include <fstream>
#include <cstring>
#include <functional>

void (*NYADecoder::NYAFunctions[NYA_BLOCK_TYPE_COUNT])(BitReader&, NYAImage*, NYA_DWord&) = {
    &decodeNYASingle,
    &decodeNYARun,
    &decodeNYAHuffmanSingle,
    &decodeNYAHuffmanRun
};
NYAHuffmanNode* NYADecoder::huffmanRoot = nullptr;
int NYADecoder::colorDepth = NYA_RGB;
int NYADecoder::filterType = 0;
NYA_Word NYADecoder::width = 0;
NYA_Word NYADecoder::height = 0;
NYA_DWord NYADecoder::previousValue = NYA_PREVIOUS_RGB;

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

    if (strncmp(reinterpret_cast<const char*>(&header.magic), "NYA!", NYA_MAGIC_LENGTH) != 0) {
        std::cerr << "File specified is either corrupted or not a valid NYA file" << std::endl;
        return nullptr;
    }

    if (header.flags & NYA_FLAG_ALPHA) {
        colorDepth = NYA_RGBA;
        previousValue = NYA_PREVIOUS_RGBA;
    }
    filterType = header.flags & NYA_FILTER_MASK;
    width = header.width;
    height = header.height;

    BitReader reader(nyaFile);
    buildHuffmanTree(reader);

    NYAImage* image = new NYAImage();
    image->width = header.width;
    image->height = header.height;

    NYA_DWord pixelCount = static_cast<NYA_DWord>(header.width) * static_cast<NYA_DWord>(header.height);
    image->pixels = new NYA_DWord[pixelCount];

    NYA_DWord pixelIndex = 0;

    while (pixelIndex < pixelCount) {
        auto tag = reader.readBits(NYA_TAG_LENGTH);
        NYAFunctions[tag](reader, image, pixelIndex);
    }

    // BARELY TAKES TIME, ITS FINE
    applyFilter(image, pixelCount);
    deleteHuffmanTree(huffmanRoot);

    return image;
}

void NYADecoder::decodeNYASingle(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex) {
    NYA_DWord value = readPixelValue(reader);
    image->pixels[pixelIndex] = value;

    pixelIndex++;
}

void NYADecoder::decodeNYARun(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex) {
    NYA_DWord value = readPixelValue(reader);
    auto length = reader.readBits(NYA_LENGTH_BITCOUNT) + 1;
    auto run = reader.readBits(length) + 1;

    for (NYA_DWord i = 0; i < run; i++) {
        image->pixels[pixelIndex] = value;
        pixelIndex++;
    }
}

void NYADecoder::decodeNYAHuffmanSingle(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex) {
    NYA_DWord value = readHuffmanValue(reader);

    image->pixels[pixelIndex] = value;

    pixelIndex++;
}

void NYADecoder::decodeNYAHuffmanRun(BitReader& reader, NYAImage* image, NYA_DWord& pixelIndex) {
    NYA_DWord value = readHuffmanValue(reader);
    auto length = reader.readBits(NYA_LENGTH_BITCOUNT) + 1;
    auto run = reader.readBits(length) + 1;

    for (NYA_DWord i = 0; i < run; i++) {
        image->pixels[pixelIndex] = value;
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

NYA_DWord NYADecoder::readPixelValue(BitReader& reader) {
    NYA_DWord value = reader.readBits(colorDepth);

    if (colorDepth == NYA_RGB) {
        value = (value << 8) | NYA_BYTE_MASK;
    }

    return value;
}

NYA_DWord NYADecoder::readHuffmanValue(BitReader& reader) {
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
    if (filterType == NYA_FILTER_UP) {
        return (width * (index % height)) + (index / height);
    }
    return index;
}

void NYADecoder::applyFilter(NYAImage* image, NYA_DWord pixelCount) {
    if (filterType == NYA_FILTER_NONE) {
        return;
    }

    for (NYA_DWord i = 0; i < pixelCount; i++) {
        NYA_DWord index = transformIndex(i);
        NYA_DWord currentValue = image->pixels[index];

        NYA_Byte prevR = (previousValue >> NYA_SHIFT_R) & NYA_BYTE_MASK;
        NYA_Byte prevG = (previousValue >> NYA_SHIFT_G) & NYA_BYTE_MASK;
        NYA_Byte prevB = (previousValue >> NYA_SHIFT_B) & NYA_BYTE_MASK;

        NYA_Byte currR = (currentValue >> NYA_SHIFT_R) & NYA_BYTE_MASK;
        NYA_Byte currG = (currentValue >> NYA_SHIFT_G) & NYA_BYTE_MASK;
        NYA_Byte currB = (currentValue >> NYA_SHIFT_B) & NYA_BYTE_MASK;

        NYA_Byte r = (prevR + currR) & NYA_BYTE_MASK;
        NYA_Byte g = (prevG + currG) & NYA_BYTE_MASK;
        NYA_Byte b = (prevB + currB) & NYA_BYTE_MASK;
        NYA_Byte a = NYA_BYTE_MASK;

        if (colorDepth == NYA_RGBA) {
            NYA_Byte prevA = previousValue & NYA_BYTE_MASK;
            NYA_Byte currA = currentValue & NYA_BYTE_MASK;

            a = (prevA + currA) & NYA_BYTE_MASK;
        }

        currentValue = (r << NYA_SHIFT_R) | (g << NYA_SHIFT_G) | (b << NYA_SHIFT_B) | a;

        image->pixels[index] = currentValue;
        previousValue = currentValue;
    }
}