#!/bin/bash

PROG_DIR=`pwd`
VERSION=`python -c 'from main import VERSION; print VERSION'`
PKG_NAME="coffee-notes-$VERSION.deb"

echo "Building package $PKG_NAME"
mkdir -p build/opt/cn
mkdir -p build/DEBIAN
mkdir -p build/usr/local/bin
mkdir -p build/usr/share/applications
mkdir -p build/usr/share/pixmaps
cp -v README.markdown icon.png *.py *.ui build/opt/cn
cp -v control build/DEBIAN
cp -v postinst build/DEBIAN
cp -v postrm build/DEBIAN
cp -v cn.desktop build/usr/share/applications
cp -v icon.png build/usr/share/pixmaps/cn.png
cd build/usr/local/bin
ln -sv ../../../opt/cn/cn.py cn
cd $PROG_DIR
pwd
dpkg -b ./build $PKG_NAME
