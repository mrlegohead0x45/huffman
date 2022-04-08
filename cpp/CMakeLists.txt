cmake_minimum_required(VERSION 3.23)

option(BUILD_WITH_VIS "Build with visualisation" OFF)
if(BUILD_WITH_VIS)
    list(APPEND VCPKG_MANIFEST_FEATURES "visualisation")
endif()
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")

project(huffman CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(huffman-srcs "src/huffman.cpp")

add_executable(huffman ${huffman-srcs})
target_include_directories(huffman PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

target_compile_options(huffman PRIVATE 
    $<$<CXX_COMPILER_ID:Clang,GNU,AppleClang>:
        -Wall -Werror -Wextra>
    $<$<CXX_COMPILER_ID:MSVC>:
        /WX /W4>
)

if(BUILD_WITH_VIS)
    target_compile_definitions(huffman PRIVATE BUILD_WITH_VIS)
endif()

find_package(argparse CONFIG REQUIRED)
target_link_libraries(huffman PRIVATE argparse::argparse)
