add_library(nyadecoder STATIC
    src/Decoder.cpp
    src/BitReader.cpp
)
target_include_directories(nyadecoder PUBLIC
    include
)