cmake_minimum_required(VERSION 3.23)

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
