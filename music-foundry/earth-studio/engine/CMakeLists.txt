cmake_minimum_required(VERSION 3.20)
project(earth_studio_audio_engine VERSION 0.1.0 LANGUAGES CXX)
add_library(earth_studio_audio_engine STATIC src/audio_engine.cpp)
target_include_directories(earth_studio_audio_engine PUBLIC include)
target_compile_features(earth_studio_audio_engine PUBLIC cxx_std_20)
set_target_properties(earth_studio_audio_engine PROPERTIES CXX_EXTENSIONS OFF)
if(MSVC)
  target_compile_options(earth_studio_audio_engine PRIVATE /W4 /permissive-)
else()
  target_compile_options(earth_studio_audio_engine PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow)
endif()
add_executable(earth_studio_engine_tests tests/audio_engine_tests.cpp)
target_link_libraries(earth_studio_engine_tests PRIVATE earth_studio_audio_engine)
enable_testing()
add_test(NAME earth_studio_engine_tests COMMAND earth_studio_engine_tests)

add_library(earth_studio_audio_c_api STATIC src/c_api.cpp)
target_link_libraries(earth_studio_audio_c_api PUBLIC earth_studio_audio_engine)
target_include_directories(earth_studio_audio_c_api PUBLIC include)
target_compile_features(earth_studio_audio_c_api PUBLIC cxx_std_20)
add_executable(earth_studio_c_api_tests tests/c_api_tests.cpp)
target_link_libraries(earth_studio_c_api_tests PRIVATE earth_studio_audio_c_api)
add_test(NAME earth_studio_c_api_tests COMMAND earth_studio_c_api_tests)

if(EMSCRIPTEN)
  add_executable(earth_studio_engine_wasm src/audio_engine.cpp src/c_api.cpp)
  target_include_directories(earth_studio_engine_wasm PRIVATE include)
  target_compile_features(earth_studio_engine_wasm PRIVATE cxx_std_20)
  set_target_properties(earth_studio_engine_wasm PROPERTIES CXX_EXTENSIONS OFF SUFFIX ".js")
  target_link_options(earth_studio_engine_wasm PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_NAME=createEarthStudioEngine"
    "-sENVIRONMENT=worker" "-sALLOW_MEMORY_GROWTH=0"
    "-sINITIAL_MEMORY=16777216" "-sFILESYSTEM=0"
    "-sEXPORTED_FUNCTIONS=['_malloc','_free','_earth_engine_create','_earth_engine_destroy','_earth_engine_render','_earth_engine_set_instrument','_earth_engine_set_master_gain','_earth_engine_active_voices']"
  )
endif()
