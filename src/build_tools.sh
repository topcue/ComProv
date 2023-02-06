#!/bin/bash

WORK_DIR=$HOME/ComProv
STORAGE=$WORK_DIR/storage

mkdir -p $STORAGE/sources
cd $STORAGE/sources
wget https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-15.0.7.tar.gz
tar -xvf llvmorg-15.0.7.tar.gz
mv llvm-project-llvmorg-15.0.7 llvm-project
cd llvm-project/llvm
rm -rf build install && mkdir -p build install && cd build

cmake .. -DCMAKE_BUILD_TYPE=Release --install-prefix=$STORAGE/sources/llvm-project/llvm/install
make -j 16
make install

cp ../install/bin/llvm-objdump $WORK_DIR/tools/


# EOF
