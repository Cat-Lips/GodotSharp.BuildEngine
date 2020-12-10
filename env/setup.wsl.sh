#!/bin/bash

echo -e '\n*** Updating Package Sources ***'
wget -O- https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
add-apt-repository -y https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod
add-apt-repository -y ppa:ubuntu-toolchain-r/test
add-apt-repository -y ppa:deadsnakes/ppa
add-apt-repository -y ppa:git-core/ppa
apt autoremove -y
apt update

echo -e '\n*** Installing .NET ***'
apt install --no-install-recommends -y dotnet-sdk-5.0

echo -e '\n*** Installing Python ***'
apt install --no-install-recommends -y python3.9 python3.9-venv python3.9-distutils
update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.9 39
python3.9 -m ensurepip
python3.9 -m pip install --upgrade pip
python3.9 -m pip install scons py-linq humanize

echo -e '\n*** Installing MXE Dependencies (full list) ***'
apt install --no-install-recommends -y autoconf automake autopoint bash bison bzip2 flex g++ g++-multilib gettext git gperf intltool libc6-dev-i386 libgdk-pixbuf2.0-dev libltdl-dev libssl-dev libtool-bin libxml-parser-perl lzip make openssl p7zip-full patch perl python ruby sed unzip wget xz-utils

echo -e '\n*** Installing Godot/Mono Dependencies ***'
apt install --no-install-recommends -y libkrb5-dev
env/setup.wsl.py
apt clean
