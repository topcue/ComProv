#!/bin/bash

WORK_DIR=$HOME/ComProv
STORAGE=$WORK_DIR/storage

mkdir -p $STORAGE/sources
cd $STORAGE/sources
wget https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-15.0.7.tar.gz
tar -xvf llvmorg-15.0.7.tar.gz
mv llvm-project-llvmorg-15.0.7 llvm-project

cd llvm-project
rm -rf build install
cmake -DCMAKE_BUILD_TYPE=Release -S llvm -B build -DCMAKE_INSTALL_PREFIX=install
cd build
make -j 8
make install

# ln -s $STORAGE/sources/llvm-project/install/bin/llvm-objdump $WORK_DIR/tools/llvm-objdump
cp $STORAGE/sources/llvm-project/install/bin/llvm-objdump $WORK_DIR/tools/llvm-objdump
cp $STORAGE/sources/llvm-project/install/bin/llvm-objcopy $WORK_DIR/tools/llvm-objcopy


# EOF
