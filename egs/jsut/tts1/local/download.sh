#!/bin/bash

# Copyright 2018 Nagoya University (Takenori Yoshimura), Ryuichi Yamamoto
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

db=$1

# check arguments
if [ $# != 1 ]; then
    echo "Usage: $0 <download_dir>"
    exit 1
fi

set -euo pipefail

cwd=$(pwd)
if [ ! -e ${db}/jsut_ver1.1 ]; then
    mkdir -p ${db}
    cd ${db}
    wget http://ss-takashi.sakura.ne.jp/corpus/jsut_ver1.1.zip
    unzip -o ./*.zip
    rm ./*.zip
    cd ${cwd}
    echo "Successfully downloaded data."
else
    echo "Already exists. Skipped."
fi

if [ ! -e ${db}/jsut_lab ]; then
    echo "Downloading full-context labels for jsut v1.1..."
    cd ${db}
    git clone https://github.com/r9y9/jsut-lab
    for name in loanword128 repeat500 voiceactress100 basic5000 onomatopee300 travel1000 countersuffix26 precedent130 utparaphrase512; do
        cp -vr jsut-lab/${name} jsut_ver1.1/
    done
    cd ${cwd}
    echo "Successfully downloaded full-context label."
else
    echo "Already exists. Skipped."
fi
