#!/bin/bash
cd `dirname $0`

version=0.4.14

for platform in darwin linux
do
    for arch in 386 amd64
    do
        wget https://dist.ipfs.io/go-ipfs/v${version}/go-ipfs_v${version}_${platform}-${arch}.tar.gz
        tar -zxvf go-ipfs_v${version}_${platform}-${arch}.tar.gz
        mkdir -p nyptune/ipfs/${platform}-${arch}
        cp go-ipfs/ipfs nyptune/ipfs/${platform}-${arch}/
        rm -rf go-ipfs
        rm go-ipfs_v${version}_${platform}-${arch}.tar.gz
    done
done
