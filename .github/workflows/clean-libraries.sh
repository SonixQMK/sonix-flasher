#!/bin/bash
cd dist/sonix-flasher
rm libgobject-2.0.so.* \
    libgio-2.0.so.* \
    libgtk-3.so.* \
    libgdk-3.so.* \
    libharfbuzz.so.* \
    libfontconfig.so.* \
    libfreetype.so.* \
    libgpg-error.so.* \
    libstdc++.so.* \
    libglib-2.0.so.*
