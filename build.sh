#!/usr/bin/env sh
platform=$(uname)
if [ "$platform" = "Linux" ]; then
    echo "Building for Linux platform..."
    mkdir -p ./build/linux/
    cd ./build/linux/
elif [ "$platform" = "Darwin" ]; then
    echo "Building for macOS (Darwin) platform..."
    mkdir -p ./build/macos/
    cd ./build/macos/
else
    echo "Unsupported platform: $platform"
    exit 1
fi
python3 -m nuitka --enable-plugin=pyside6,upx --follow-imports --nofollow-import-to=PyQt5 --include-module=shubcrawler,passlib.handlers ../../src/shubcrawler-gui
