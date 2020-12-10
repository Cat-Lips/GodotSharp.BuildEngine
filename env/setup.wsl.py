#!/usr/bin/env python3.9

# Copied from https://github.com/godotengine/build-containers
_build_container_dependencies = {k: v.lower().replace('-devel', '-dev') for k,v in {
    'android': 'java-1.8.0-openjdk-devel ncurses-compat-libs',
    'base': 'bash bzip2 curl git make nano patch pkgconfig python-unversioned-command python3-pip unzip which xz',
    'export': 'xorg-x11-server-Xvfb mesa-dri-drivers libXcursor libXinerama libXrandr libXi alsa-lib pulseaudio-libs java-1.8.0-openjdk-devel',
    'ios': 'automake autoconf clang gcc gcc-c++ gcc-objc gcc-objc++ cmake libicu-devel libtool libxml2-devel llvm-devel openssl-devel perl python yasm',
    'javascript': 'java-openjdk',
    'mono': 'gcc gcc-c++ make yasm autoconf automake cmake gettext libtool perl',
    'mono_glue': 'xorg-x11-server-Xvfb libX11-devel libXcursor-devel libXrandr-devel libXinerama-devel libXi-devel alsa-lib-devel pulseaudio-libs-devel libudev-devel mesa-libGL-devel mesa-libGLU-devel mesa-dri-drivers',
    'msvc': 'wine winetricks xorg-x11-server-Xvfb p7zip-plugins findutils',
    'osx': 'automake autoconf bzip2-devel clang libicu-devel libtool libxml2-devel llvm-devel openssl-devel yasm',
    'ubuntu': 'autoconf automake bzip2 cmake curl gettext git libtool make perl scons xz-utils gcc-9 g++-9 libudev-dev libx11-dev libxcursor-dev libxrandr-dev libasound2-dev libpulse-dev libgl1-mesa-dev libglu1-mesa-dev libxi-dev libxinerama-dev yasm',
    'windows': 'mingw32-gcc mingw32-gcc-c++ mingw32-winpthreads-static mingw64-gcc mingw64-gcc-c++ mingw64-winpthreads-static wine',
    'xcode': 'autoconf automake libtool clang cmake fuse fuse-devel libxml2-devel libicu-devel compat-openssl10-devel bzip2-devel kmod cpio',
}.items()}

_fedora_to_ubuntu_package_map = {
    'llvm-dev': 'llvm',
    'pkgconfig': 'pkg-config',
    'alsa-lib-dev': 'libasound2-dev',
    'mesa-libgl-dev': 'libgl1-mesa-dev',
    'mesa-libglu-dev': 'libglu1-mesa-dev',
    'pulseaudio-libs-dev': 'libpulse-dev',
}

_dependencies = {
    'Tools': 'gettext git patch pkg-config yasm',
    'Build': 'autoconf automake clang cmake g++-9 gcc-9 llvm make',
    'Libs': 'bzip2 libasound2-dev libgl1-mesa-dev libglu1-mesa-dev libicu-dev libpulse-dev libtool libudev-dev libxcursor-dev libx11-dev libxi-dev libxinerama-dev libxml2-dev libxrandr-dev',
}

_ignore = {
    'build': 'gcc gcc-c++ gcc-objc gcc-objc++ scons',
    'system': 'bash curl nano perl unzip which xz xz-utils',
    'python': 'python python-unversioned-command python3-pip',
    'mingw32': 'mingw32-gcc mingw32-gcc-c++ mingw32-winpthreads-static',
    'mingw64': 'mingw64-gcc mingw64-gcc-c++ mingw64-winpthreads-static',
    'libs': 'alsa-lib bzip2-dev libxcursor libxi libxinerama libxrandr mesa-dri-drivers pulseaudio-libs xorg-x11-server-xvfb',
}

_todo = {
    'android': 'java-1.8.0-openjdk-dev ncurses-compat-libs',
    'ios/osx': 'openssl-dev',
    'javascript': 'java-openjdk',
    'msvc': 'findutils p7zip-plugins wine winetricks',
    'xcode': 'compat-openssl10-dev cpio fuse fuse-dev kmod',
}

import utils

class Dependencies:

    @staticmethod
    def install():
        dependencies = ' '.join(_dependencies.values())
        utils.execute(f'apt install --no-install-recommends -y {dependencies}')
        utils.execute('update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9')

    @staticmethod
    def validate(print_used=False):
        from py_linq import Enumerable

        def initialise():
            for k,v in _build_container_dependencies.items():
                for fedora_lib, ubuntu_lib in _fedora_to_ubuntu_package_map.items():
                    v = v.replace(fedora_lib, ubuntu_lib)
                _build_container_dependencies[k] = v

        def split(source):
            return Enumerable(source.values())\
                .select_many(lambda x: x.split())

        def _log(items, source):
            def get_keys(source, x):
                return ', '.join([k for k,v in source.items() if x in v.split()])

            print('\n'.join(Enumerable(sorted(items))
                .select(lambda x: f'{x} ({get_keys(source, x)})')))

        initialise()

        required_dependencies = set(split(_build_container_dependencies))
        known_dependencies = set(split(_dependencies|_ignore|_todo))
        missing_dependencies = required_dependencies - known_dependencies
        unexpected_dependencies = known_dependencies - required_dependencies

        if missing_dependencies or unexpected_dependencies:
            print(f'\nError: Godot Build Containers has {len(required_dependencies)} dependencies:')
            _log(required_dependencies, _build_container_dependencies)
            if missing_dependencies:
                print(f'\nWSL has {len(missing_dependencies)} missing dependencies:')
                _log(missing_dependencies, _build_container_dependencies)
            if unexpected_dependencies:
                print(f'\nWSL has {len(unexpected_dependencies)} unexpected dependencies:')
                _log(unexpected_dependencies, _dependencies|_ignore|_todo)
            print(f'\n*** Dependency Validation FAILED ***')
            return False

        if print_used:
            used_dependencies = set(split(_dependencies))
            print(f'\nDependencies ({len(used_dependencies)}):')
            used_dependencies = [x for x in used_dependencies]
            _log(used_dependencies, _dependencies)

        return True

if __name__ == '__main__':
    if Dependencies.validate():
        Dependencies.install()
