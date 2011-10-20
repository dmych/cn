#!/bin/bash

PROG_DIR=`pwd`
VERSION=`python -c 'from main import VERSION; print VERSION'`
PKG_NAME="coffee-notes-$VERSION.deb"

echo "Building package $PKG_NAME"
mkdir -p build/opt/cn
mkdir -p build/DEBIAN
mkdir -p build/usr/local/bin
cp -v README.markdown icon.png *.py *.ui build/opt/cn
cp -v control build/DEBIAN
cd build/usr/local/bin
ln -sv ../../../opt/cn/cn.py cn
cd $PROG_DIR
pwd
dpkg -b ./build $PKG_NAME
