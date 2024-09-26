#include "BitReader.hpp"

BitReader::BitReader(std::ifstream &stream) : m_FileStream(stream), m_CurrentByte(0), m_BitPos(8) { }

bool BitReader::readBit() {
    if (m_BitPos == 8) {
        m_FileStream.read(reinterpret_cast<char*>(&m_CurrentByte), 1);
        m_BitPos = 0;
    }
    bool bit = (m_CurrentByte >> (7 - m_BitPos)) & 1;
    m_BitPos++;
    return bit;
}

uint32_t BitReader::readBits(int n) {
    uint32_t result = 0;
    for (int i = 0; i < n; ++i) {
        result = (result << 1) | readBit();
    }
    return result;
}
