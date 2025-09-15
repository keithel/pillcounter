cmake_minimum_required(VERSION 3.16)
project(pillcounter VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(PROJECT_BINARY_NAME "app${CMAKE_PROJECT_NAME}")

find_package(QT NAMES Qt6 REQUIRED COMPONENTS Core)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui QuickControls2 Qml)
# find_package(Qt${QT_VERSION_MAJOR} COMPONENTS LinguistTools)

qt_standard_project_setup(
    I18N_TRANSLATED_LANGUAGES de en es fr
    I18N_SOURCE_LANGUAGE en
)

set(qml_module_uri ${PROJECT_NAME})

qt_policy(SET QTP0001 NEW)
qt_policy(SET QTP0004 NEW)

qt_add_executable(${PROJECT_BINARY_NAME} WIN32 MACOSX_BUNDLE
    src/main.cpp
)

# Add this later when translations are desired
# qt_add_translations(
#     TARGETS ${PROJECT_BINARY_NAME}
#     TS_FILE_BASE lang
# )

qt_add_qml_module(${PROJECT_BINARY_NAME}
    URI ${qml_module_uri}
    VERSION 1.0
    QML_FILES
        "src/pillcounter/Main.qml"
    #RESOURCES
        # List relative path to resources here
    SOURCES
        src/appconfig.h
        src/appconfig.cpp
    OUTPUT_DIRECTORY pillcounter
)

target_include_directories(${PROJECT_BINARY_NAME}
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src
)

qt_add_resources(${PROJECT_BINARY_NAME} "resources"
    PREFIX "/"
    FILES
)

# This is so that in C++, you can provide path to resources without hardcoding the resource
# prefix. It's possible this may be able to be created just from within C++ - as you probably
# can get the module URI, then do the .->/ replacement in C++, so I guess this is the lazy
# approach.
string(REPLACE "." "/" qml_module_resource_path "${qml_module_uri}/")
target_compile_definitions(${PROJECT_BINARY_NAME} PRIVATE
    RESOURCE_PREFIX="${qml_module_resource_path}"
)

target_link_libraries(${PROJECT_BINARY_NAME} PUBLIC
    Qt::Core
    Qt::Gui
    Qt::QuickControls2
    Qt::Qml
)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
if(${QT_VERSION} VERSION_LESS 6.1.0)
  set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER ${qml_module_uri})
endif()

set_target_properties(${PROJECT_BINARY_NAME} PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)
