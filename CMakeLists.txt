# vim:et:ts=4:sw=4:cc=120
#[======================================================================[.rst:
~~~~~~~~~~~~~~~~~~~
Lua-CMake-Autobuild
~~~~~~~~~~~~~~~~~~~

A single-file solution for Lua CMake build
------------------------------------------

This file may be simply dropped to the empty subdirectory of another
CMake project and added by add_subdirectory.
Only Lua runtime will be added to the install.

All the sources are downloaded automatically from the official Lua web site
using the version set in ``project``

When it is used standalone, this file builds a full Lua distribution.
However, it may be easily configured to provide only the neccessary parts

All the installable artifacts are assigned to components,
so it is possible to make a confurable installer by CPack and NSIS/WiX

CMake options and variables
-----------------------------

+-----------------------+----------------------------------------------------+
| Variable              | Description                                        |
+=======================+====================================================+
| LUA_BUILD_SHARED      | Build Lua library as a shared library              |
|                       | (OFF by default)                                   |
+-----------------------+----------------------------------------------------+
| LUA_BUILD_AS_CXX      | Build Lua by C++ compiler i.e. use C++ exceptions  |
|                       | (OFF by default)                                   |
+-----------------------+----------------------------------------------------+
| LUA_EXPORT_C_ABI      | Export C ABI for C++ built Lua i.e. the exports    |
|                       | are the same as for Lua built by C compiler        |
|                       | This is a default behavior for C++ build           |
+-----------------------+----------------------------------------------------+
| LUA_BUILD_INTERPRETER | Build Lua interpreter (ON for standalone build)    |
+-----------------------+----------------------------------------------------+
| LUA_BUILD_COMPILER    | Build Lua compiler (ON for standalone build)       |
+-----------------------+----------------------------------------------------+
| LUA_BUILD_TESTING     | Enable Lua basic test suite                        |
|                       | (ON for standalone build)                          |
+-----------------------+----------------------------------------------------+
| LUA_TESTSUITE_VERSION | The version of the Lua test suite, determined      |
|                       | automatically if is not set                        |
+-----------------------+----------------------------------------------------+
| LUA_UNITY_BUILD       | Enable Unity build for Lua library (experimental)  |
|                       | (OFF by default)                                   |
+-----------------------+----------------------------------------------------+
| LUA_DEBUG_POSTFIX     | Output filenames postfix for Debug configuration   |
+-----------------------+----------------------------------------------------+
| LUA_INSTALL_DOCS      | Enable installation of docs                        |
|                       | (available only for standalone, ON by default)     |
+-----------------------+----------------------------------------------------+
| LUA_INSTALL_DEBINFO   | Enable installation of PDBs and packaging          |
|                       | of unstripped ELFs (available only for standalone) |
+-----------------------+----------------------------------------------------+

Available Targets
-----------------
- Lua::Library
- Lua::Interpreter
- Lua::Compiler

** This file doesn't provide the same variables as the standard FindLua **

License
-------

The project is licensed under the [MIT license][license]

Copyright (c) 2023 Alexander Voronkov

#=====]======================================================================]
#[===========================================================================[
MIT License

Copyright (c) 2023 Alexander Voronkov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#]===========================================================================]

cmake_minimum_required(VERSION 3.21...3.26)

project(lua LANGUAGES C VERSION 5.4.4)
include(CTest)
include(GNUInstallDirs)
include(CMakeDependentOption)

option(LUA_BUILD_AS_CXX "Build Lua by C++ compiler" OFF)
cmake_dependent_option(LUA_EXPORT_C_ABI "Export C ABI for C++ built Lua" ON LUA_BUILD_AS_CXX OFF)
option(LUA_BUILD_SHARED "Build Lua library as a shared library" ${BUILD_SHARED_LIBS})
option(LUA_UNITY_BUILD "Enable unity build for Lua library" OFF)

if(BUILD_TESTING AND PROJECT_IS_TOP_LEVEL)
    set(lua_testing_default ON)
endif()

# LUA_TESTSUITE_VERSION may be set to avoid testsuite version autodetection
option(LUA_BUILD_TESTING "Enable Lua build testing" ${lua_testing_default})
option(LUA_BUILD_INTERPRETER "Build Lua interpreter" ${PROJECT_IS_TOP_LEVEL})
option(LUA_BUILD_COMPILER "Build Lua compiler" ${PROJECT_IS_TOP_LEVEL})
set(LUA_DEBUG_POSTFIX D CACHE STRING "Postfix for Lua Debug outputs")

if(PROJECT_IS_TOP_LEVEL)
    option(LUA_INSTALL_DOCS "If the Lua docs and manpages(in Unix) shall be installed" ON)
    option(LUA_INSTALL_DEBINFO "If the Lua debug information shall be preserved for installation" ON)
endif()

set(versioned_name ${PROJECT_NAME}-${PROJECT_VERSION})
set(sources_tar ${versioned_name}.tar.gz)
set(luaconf_h ${CMAKE_CURRENT_SOURCE_DIR}/${versioned_name}/src/luaconf.h)
set(luaconf_h_in ${luaconf_h}.in)

if(PROJECT_IS_TOP_LEVEL AND UNIX AND NOT APPLE AND NOT CMAKE_INSTALL_RPATH)
    set(CMAKE_INSTALL_RPATH $ORIGIN $ORIGIN/../lib)
endif()

if(PROJECT_IS_TOP_LEVEL)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

get_property(lua_debug_configs GLOBAL PROPERTY DEBUG_CONFIGURATIONS)
if(NOT lua_debug_configs)
    set(lua_debug_configs Debug)
endif()

set(lua_release_configs ${CMAKE_CONFIGURATION_TYPES})
if(lua_release_configs)
    list(REMOVE_ITEM lua_release_configs ${lua_debug_configs})
else()
    set(lua_release_configs Release RelWithDebInfo MinSizeRel)
endif()

macro(download_with_log url file progress)
    file(DOWNLOAD ${url} ${file} ${progress} STATUS status LOG log)
    file(APPEND ${CMAKE_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/CMakeOutput.log
        "Transmission log for ${url}:\n${log}\n\n")
    list(POP_FRONT status code)
endmacro()

function(download_tar base_url tar)
    message(STATUS "Downloading ${tar}")
    download_with_log(${base_url}/${tar} ${CMAKE_CURRENT_BINARY_DIR}/${tar} SHOW_PROGRESS)
    if(NOT code EQUAL 0)
        message(FATAL_ERROR "Download failed: ${http_status}")
    endif()
endfunction()


if(NOT IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${versioned_name})
    download_tar(https://www.lua.org/ftp ${sources_tar})
    file(ARCHIVE_EXTRACT INPUT ${CMAKE_CURRENT_BINARY_DIR}/${sources_tar}
        DESTINATION ${CMAKE_CURRENT_SOURCE_DIR} VERBOSE)
    file(COPY_FILE ${luaconf_h} ${luaconf_h}.bak)
    file(READ ${luaconf_h} luaconf)
    string(REGEX REPLACE "([ \t]*#if[ \t]+defined\\(LUA_BUILD_AS_DLL\\))" [[@lua_conf_code@\1]] luaconf "${luaconf}")
    string(REGEX REPLACE "([ \t]*#define[ \t]+LUA_API[ \t]+)[^ \t\n_]+" [[\1@lua_api_extern_2@]] luaconf "${luaconf}")
    string(REGEX REPLACE "([ \t]*#define[ \t]+LUA_API[ \t]+)__" [[\1@lua_api_extern_1@__]] luaconf "${luaconf}")
    file(WRITE ${luaconf_h_in} "${luaconf}")
endif()

file(STRINGS ${versioned_name}/Makefile to_inc REGEX "^TO_INC=.+" LIMIT_COUNT 1)
if(NOT to_inc)
    message(FATAL_ERROR "Failed to get public includes list")
endif()
string(REGEX REPLACE "[= \t]+" ";" lua_public_headers "${to_inc}")
list(POP_FRONT lua_public_headers)
list(TRANSFORM lua_public_headers PREPEND "${versioned_name}/src/")

file(STRINGS ${versioned_name}/src/Makefile makefile)
string(REPLACE "\;" "" makefile "${makefile}")
list(FILTER makefile INCLUDE REGEX "^(LUA|LUAC|CORE|LIB)_O=.+")
foreach(l IN LISTS makefile)
    string(REGEX REPLACE "[= \t]+" ";" files "${l}")
    list(POP_FRONT files name)
    string(REPLACE "_O" "_sources" name "${name}")
    list(TRANSFORM files REPLACE "(.+).o" "${versioned_name}/src/\\1.c")
    set(${name} "${files}")
endforeach()

if(LUA_BUILD_AS_CXX)
    enable_language(CXX)
    set_source_files_properties(
        ${LIB_sources} ${CORE_sources}
        ${LUA_sources} ${LUAC_sources}
        PROPERTIES LANGUAGE CXX)
endif()

if(LUA_EXPORT_C_ABI)
    set(lua_conf_code [[
#ifdef __cplusplus
#define LUA_API_EXTERN extern "C"
#else
#define LUA_API_EXTERN extern
#endif
]])
    set(lua_api_extern_1 "LUA_API_EXTERN ")
    set(lua_api_extern_2 LUA_API_EXTERN)
else()
    set(lua_conf_code "")
    set(lua_api_extern_1 "")
    set(lua_api_extern_2 extern)
endif()
configure_file(${luaconf_h_in} ${luaconf_h} @ONLY NEWLINE_STYLE LF)


add_library(lua-platform INTERFACE)

add_library(lua-obj OBJECT EXCLUDE_FROM_ALL)
target_sources(lua-obj PRIVATE ${LIB_sources} ${CORE_sources})
target_link_libraries(lua-obj PUBLIC lua-platform)

if(LUA_BUILD_SHARED)
    add_library(lua-lib SHARED)
    add_library(lua-luaclib ALIAS lua-obj)
    set_target_properties(lua-obj PROPERTIES
        POSITION_INDEPENDENT_CODE ON)
else()
    add_library(lua-lib STATIC)
    add_library(lua-luaclib ALIAS lua-lib)
endif()

set(lua_sources_path ${CMAKE_CURRENT_SOURCE_DIR}/${versioned_name}/src)

target_include_directories(lua-lib INTERFACE
    $<BUILD_INTERFACE:${lua_sources_path}>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

add_library(Lua::Library ALIAS lua-lib)
set_target_properties(lua-lib PROPERTIES
    EXPORT_NAME Library
    DEBUG_POSTFIX ${LUA_DEBUG_POSTFIX}
    VERSION ${PROJECT_VERSION}
    SOVERSION 0)

if(WIN32)
    string(REPLACE ";" "," genex_deb_confs "${lua_debug_configs}")
    if(LUA_BUILD_SHARED)
        target_sources(lua-lib PRIVATE ${LIB_sources} ${CORE_sources})
        target_link_libraries(lua-lib PRIVATE lua-platform)
        target_compile_definitions(lua-lib PUBLIC LUA_BUILD_AS_DLL)
    else()
        target_link_libraries(lua-lib PRIVATE lua-obj)
        if(PROJECT_IS_TOP_LEVEL AND LUA_INSTALL_DEBINFO)
            # Use CMake 3.25+ for this
            set_property(TARGET lua-obj lua-lib PROPERTY
                MSVC_DEBUG_INFORMATION_FORMAT $<$<CONFIG:${genex_deb_confs},RelWithDebInfo>:Embedded>)
        endif()
    endif()
    # Add SourceLink information into PDB if the toolset is enough new
    if(MSVC_TOOLSET_VERSION GREATER 141 AND LUA_INSTALL_DEBINFO)
        cmake_path(APPEND lua_sources_path "*" OUTPUT_VARIABLE src_pattern)
        string(REPLACE "/" [[\\]] src_pattern ${src_pattern})
        set(sourcelink_path ${CMAKE_CURRENT_BINARY_DIR}/lua-sourcelink.json)
        file(WRITE ${sourcelink_path} [[{"documents": {]]
            "\"${src_pattern}\": \"https://raw.githubusercontent.com/lua/lua/v${PROJECT_VERSION}/*\"}}")
        cmake_path(NATIVE_PATH sourcelink_path sourcelink_path)
        target_link_options(lua-platform INTERFACE /SOURCELINK:${sourcelink_path})
    endif()
    if(MSVC AND PROJECT_VERSION MATCHES "^5.4.")
        if(CMAKE_SIZEOF_VOID_P EQUAL 8 AND PROJECT_VERSION_PATCH GREATER 1)
            target_compile_definitions(lua-platform INTERFACE $<$<CONFIG:${genex_deb_confs}>:LUAI_MAXCCALLS=165>)
        elseif(CMAKE_SIZEOF_VOID_P EQUAL 8)
            target_compile_definitions(lua-platform INTERFACE $<$<CONFIG:${genex_deb_confs}>:LUAI_MAXCSTACK=250>)
        else()
            target_compile_definitions(lua-platform INTERFACE $<$<CONFIG:${genex_deb_confs}>:LUAI_MAXCSTACK=350>)
        endif()
    endif()
    set_target_properties(lua-lib PROPERTIES
        INTERFACE_LINK_LIBRARIES ""
        OUTPUT_NAME lua${PROJECT_VERSION_MAJOR}${PROJECT_VERSION_MINOR})
elseif(UNIX)
    target_link_libraries(lua-lib PRIVATE lua-obj)
    set_target_properties(lua-lib PROPERTIES
        INTERFACE_LINK_LIBRARIES ""
        OUTPUT_NAME lua-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR})
    if(NOT APPLE)
        find_library(LUA_MATH_LIBRARY m)
        mark_as_advanced(LUA_MATH_LIBRARY)
        if(LUA_MATH_LIBRARY)
            target_link_libraries(lua-lib PRIVATE m)
            target_link_libraries(lua-obj PRIVATE m)
        endif()
    endif()
    if(APPLE)
        target_compile_definitions(lua-platform INTERFACE LUA_USE_MACOSX)
    elseif(CMAKE_SYSTEM_NAME MATCHES Linux)
        target_compile_definitions(lua-platform INTERFACE LUA_USE_LINUX)
        target_link_libraries(lua-obj INTERFACE dl)
    else()
        target_compile_definitions(lua-platform INTERFACE LUA_USE_POSIX)
    endif()
else()
    message(FATAL_ERROR "Unsupported System")
endif()



if(PROJECT_IS_TOP_LEVEL)
    set_target_properties(lua-lib PROPERTIES
        PUBLIC_HEADER "${lua_public_headers}")

    install(TARGETS lua-lib
        EXPORT LuaD
        CONFIGURATIONS ${lua_debug_configs}
        COMPONENT LuaDev)

    set(install_cmakedir ${CMAKE_INSTALL_LIBDIR}/cmake/Lua)
    set(install_configfile LuaConfig.cmake)

    install(TARGETS lua-lib
        EXPORT Lua
        CONFIGURATIONS ${lua_release_configs}
        RUNTIME
            COMPONENT LuaRuntime
        LIBRARY
            COMPONENT LuaRuntime
            NAMELINK_COMPONENT LuaDev
        ARCHIVE
            COMPONENT LuaDev
        PUBLIC_HEADER
            COMPONENT LuaDev)

    if(LUA_INSTALL_DOCS)
        install(DIRECTORY ${versioned_name}/doc/
            TYPE DOC
            CONFIGURATIONS ${lua_release_configs}
            COMPONENT LuaDoc
            PATTERN *.1 EXCLUDE)
    endif()

    install(EXPORT Lua
        FILE ${install_configfile}
        CONFIGURATIONS ${lua_release_configs}
        DESTINATION ${install_cmakedir}
        COMPONENT LuaDev
        NAMESPACE Lua::)

    install(EXPORT LuaD
        FILE ${install_configfile}
        CONFIGURATIONS ${lua_debug_configs}
        DESTINATION ${install_cmakedir}
        COMPONENT LuaDev
        NAMESPACE Lua::)

    include(CMakePackageConfigHelpers)
    write_basic_package_version_file(LuaConfigVersion.cmake
        COMPATIBILITY SameMinorVersion)

    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/LuaConfigVersion.cmake
        DESTINATION ${install_cmakedir}
        COMPONENT LuaDev)
elseif(LUA_BUILD_SHARED)
    install(TARGETS lua-lib
        EXPORT Lua
        RUNTIME
            DESTINATION ${CMAKE_INSTALL_BINDIR}
            COMPONENT LuaRuntime
        LIBRARY
            DESTINATION ${CMAKE_INSTALL_LIBDIR}
            COMPONENT LuaRuntime
            NAMELINK_SKIP)
endif()

if(LUA_UNITY_BUILD)
    set_source_files_properties(${LIB_sources} PROPERTIES UNITY_GROUP LUA_LIB)
    set_source_files_properties(${CORE_sources} PROPERTIES UNITY_GROUP LUA_CORE)
    foreach(t IN ITEMS lua-obj lua-lib)
        set_target_properties(${t} PROPERTIES
            UNITY_BUILD_MODE GROUP
            UNITY_BUILD ON)
    endforeach()
endif()

if(LUA_BUILD_INTERPRETER OR LUA_BUILD_TESTING)
    add_executable(lua-lua ${LUA_sources})
    target_link_libraries(lua-lua PRIVATE lua-lib lua-platform)
    if(UNIX)
        include(CheckIncludeFile)
        check_include_file("readline/readline.h" HAVE_READLINE_H)
        if(HAVE_READLINE_H)
            target_compile_definitions(lua-lua PRIVATE LUA_USE_READLINE)
            target_link_libraries(lua-lua PRIVATE readline)
        endif()
    endif()
    add_executable(Lua::Interpreter ALIAS lua-lua)
    set_target_properties(lua-lua PROPERTIES
        EXPORT_NAME Interpreter
        DEBUG_POSTFIX ${LUA_DEBUG_POSTFIX}
        OUTPUT_NAME lua)
endif()

if(LUA_BUILD_INTERPRETER)
    install(TARGETS lua-lua
        EXPORT Lua
        CONFIGURATIONS ${lua_release_configs}
        COMPONENT LuaInterpreter)
    if(PROJECT_IS_TOP_LEVEL)
        install(TARGETS lua-lua
            EXPORT LuaD
            CONFIGURATIONS ${lua_debug_configs}
            COMPONENT LuaDev
            )
            if(UNIX AND LUA_INSTALL_DOCS)
            install(FILES ${versioned_name}/doc/lua.1
                TYPE MAN
                CONFIGURATIONS ${lua_release_configs}
                COMPONENT LuaMan)
        endif()
    endif()
endif()

if(LUA_BUILD_COMPILER)
    add_executable(lua-luac ${LUAC_sources})
    target_link_libraries(lua-luac PRIVATE lua-luaclib lua-platform)
    add_executable(Lua::Compiler ALIAS lua-luac)
    set_target_properties(lua-luac PROPERTIES
        EXPORT_NAME Compiler
        DEBUG_POSTFIX ${LUA_DEBUG_POSTFIX}
        OUTPUT_NAME luac)
    install(TARGETS lua-luac
        EXPORT Lua
        CONFIGURATIONS ${lua_release_configs}
        COMPONENT LuaCompiler)
    if(PROJECT_IS_TOP_LEVEL)
        install(TARGETS lua-luac
            EXPORT LuaD
            CONFIGURATIONS ${lua_debug_configs}
            COMPONENT LuaDev)
        if(UNIX AND LUA_INSTALL_DOCS)
            install(FILES ${versioned_name}/doc/luac.1
                TYPE MAN
                CONFIGURATIONS ${lua_release_configs}
                COMPONENT LuaMan)
        endif()
    endif()
endif()

if(LUA_BUILD_TESTING)
    enable_testing()
    set(base_url https://www.lua.org/tests)
    if(NOT LUA_TESTSUITE_VERSION)
        message(CHECK_START "Lua test suite version is not defined, searching")
        list(APPEND CMAKE_MESSAGE_INDENT "  ")
        foreach(v RANGE ${PROJECT_VERSION_PATCH} 0 -1)
            set(version ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${v})
            message(CHECK_START "Trying ${version}")
            set(versioned_name ${PROJECT_NAME}-${version}-tests)
            set(tests_tar ${versioned_name}.tar.gz)
            set(tests_tar_abs ${CMAKE_CURRENT_BINARY_DIR}/${tests_tar})
            download_with_log(${base_url}/${tests_tar} ${tests_tar_abs} "")
            if(code EQUAL 0)
                message(CHECK_PASS "found")
                set(LUA_TESTSUITE_VERSION ${version} CACHE STRING
                    "The version of Lua test suite used for testing")
                break()
            else()
                file(REMOVE ${tests_tar_abs})
                message(CHECK_FAIL "not found")
            endif()
        endforeach()
        list(POP_BACK CMAKE_MESSAGE_INDENT)
        if(LUA_TESTSUITE_VERSION)
            message(CHECK_PASS "found ${LUA_TESTSUITE_VERSION}")
        else()
            message(CHECK_FAIL "no suitable version found")
        endif()
    endif()
    if(NOT LUA_TESTSUITE_VERSION STREQUAL PROJECT_VERSION)
        message(WARNING "Using Lua test suite ${LUA_TESTSUITE_VERSION} for Lua ${PROJECT_VERSION}")
    endif()
    set(versioned_name ${PROJECT_NAME}-${LUA_TESTSUITE_VERSION}-tests)
    set(tests_tar ${versioned_name}.tar.gz)
    set(tests_tar_abs ${CMAKE_CURRENT_BINARY_DIR}/${tests_tar})
    set(tests_dir ${CMAKE_CURRENT_SOURCE_DIR}/${versioned_name})
    if(NOT IS_DIRECTORY ${tests_dir})
        if(NOT EXISTS ${tests_tar_abs})
            download_tar(${base_url} ${tests_tar})
        endif()
        file(ARCHIVE_EXTRACT INPUT ${tests_tar_abs}
            DESTINATION ${CMAKE_CURRENT_SOURCE_DIR} VERBOSE)
    endif()
    add_test(NAME lua-basic-test COMMAND Lua::Interpreter -e "_U=true" all.lua WORKING_DIRECTORY ${tests_dir})
endif()


if(PROJECT_IS_TOP_LEVEL)
    if(LUA_INSTALL_DEBINFO)
        set(CPACK_STRIP_FILES OFF)
        install(FILES $<$<STREQUAL:$<TARGET_PROPERTY:lua-lib,TYPE>,SHARED_LIBRARY>:$<TARGET_PDB_FILE:lua-lib>>
            $<$<BOOL:${LUA_BUILD_INTERPRETER}>:$<TARGET_PDB_FILE:lua-lua>>
            $<$<TARGET_EXISTS:lua-luac>:$<TARGET_PDB_FILE:lua-luac>>
            DESTINATION ${CMAKE_INSTALL_BINDIR}
            COMPONENT LuaDev
            OPTIONAL)
    else()
        set(CPACK_STRIP_FILES ON)
    endif()
    if(LUA_BUILD_COMPILER AND LUA_BUILD_SHARED)
        set(CPACK_COMPONENT_LUAINTERPRETER_DEPENDS LuaRuntime)
    endif()
    include(CPack)
endif()

