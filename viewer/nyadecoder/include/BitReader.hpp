#include <fstream>

class BitReader {
public:
    BitReader(std::ifstream &stream);

    bool readBit();
    uint32_t readBits(int n);
private:
    std::ifstream &m_FileStream;
    uint8_t m_CurrentByte;
    int m_BitPos;
};
