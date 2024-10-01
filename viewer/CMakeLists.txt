cmake_minimum_required(VERSION 3.5)

if(CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_CURRENT_BINARY_DIR)
    message(FATAL_ERROR "Prevented in-tree build. Please create a build directory and run the command \"cmake ..\" from there")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    message("Setting build type to 'Release' as none was specified.")
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose a build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug" OR CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    if(MSVC)
        add_compile_options(/W4)
    else()
        add_compile_options(-Wall -Wextra -pedantic)
    endif()
endif()

project(nyaviewer VERSION 1.0.1)

find_package(SDL2 REQUIRED)

add_subdirectory(nyadecoder)

set(SOURCES
    src/main.cpp
)

if (WIN32)
    enable_language("RC")
    set (WIN32_RESOURCES ${CMAKE_CURRENT_SOURCE_DIR}/nyaviewer.rc)

    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(CMAKE_INSTALL_PREFIX "C:/Program Files/nyaviewer" CACHE PATH "Set the install path prefix" FORCE)
    endif()
endif()

add_executable(nyaviewer ${SOURCES} ${WIN32_RESOURCES})

target_include_directories(nyaviewer 
    PRIVATE
        ${SDL2_INCLUDE_DIRS}
)

target_link_libraries(nyaviewer 
    PRIVATE 
        nyadecoder
        ${SDL2_LIBRARIES}
)

# INSTALL RULES

install(TARGETS nyaviewer
    RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/assets
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)