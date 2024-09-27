cmake_minimum_required(VERSION 3.0)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

project(nyaviewer VERSION 1.0.1)

find_package(SDL2 REQUIRED)

add_subdirectory(nyadecoder)

set(SOURCES
    src/main.cpp
)

add_executable(nyaviewer ${SOURCES})

target_include_directories(nyaviewer 
    PRIVATE
        ${SDL2_INCLUDE_DIRS}
)

target_link_libraries(nyaviewer 
    PRIVATE 
        nyadecoder
        ${SDL2_LIBRARIES}
)