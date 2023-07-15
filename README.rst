~~~~~~~~~~~~~~~~~~~
Lua-CMake-Autobuild
~~~~~~~~~~~~~~~~~~~

A single-file solution for Lua CMake build
------------------------------------------

This file may be simply dropped to the empty subdirectory of another
CMake project and added by add_subdirectory.
Only Lua runtime will be added to the install.

All the sources are downloaded automatically from the official
`Lua web site <http://www.lua.org/>`_ using the version set in ``project``

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
| LUA_VERSION           | The version of Lua to build                        |
|                       | (The hardcoded value is used by default)           |
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

**This file doesn't provide the same variables as the standard FindLua**

License
-------

The project is licensed under the `MIT license <LICENSE>`_

Copyright (c) 2023 Alexander Voronkov

