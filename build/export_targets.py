from config import godot_version
linuxbsd = 'x11' if godot_version and godot_version[0].isdigit() and int(godot_version[0]) <= 3 else 'linuxbsd'

# Mono export targets extracted from https://github.com/godotengine/godot-mono-builds
# Godot export targets extracted from https://docs.godotengine.org/en/latest/development/compiling/index.html
# key=platform, value=arch (expressed as Godot|Mono - no separator implies same for both)
export_targets = {
    'windows': ('bits=32|x86', 'bits=64|x86_64'),
    f'{linuxbsd}|linux': ('bits=32|x86', 'bits=64|x86_64'), # Godot4=linuxbsd, Godot3=x11
    'osx': ('arch=x86_64|x86_64'), # Also: arch=arm64|?
    'android':
    (
        'android_arch=armv7|armeabi-v7a', 'android_arch=arm64v8|arm64-v8a', # runtime_targets
        'android_arch=x86|x86', 'android_arch=x86_64|x86_64', # runtime_targets
        #'cross-arm', 'cross-arm64', 'cross-x86', 'cross-x86_64', # cross_targets
        #'cross-arm-win', 'cross-arm64-win', 'cross-x86-win', 'cross-x86_64-win' # cross_mxe_targets
    ),
    'iphone|ios':
    (
        'arch=arm|armv7', 'arch=arm64|arm64', # device_targets
        'arch=x86_64|x86_64', # sim_target (also ?|x86)
        #'cross-armv7', 'cross-arm64' # cross_targets
    ),
    'javascript|wasm':
    (
        'javascript_eval=no|runtime',
        'javascript_eval=no threads_enabled=yes|runtime-threads',
        #'?|runtime-dynamic'
    )
}

from collections import namedtuple
Arch = namedtuple('Arch', 'godot, mono')
Platform = namedtuple('Platform', 'godot, mono')
Target = namedtuple('Target', 'platform, arch')

def yield_export_targets(target_platform=None, target_arch=None):
    for platform, archs in export_targets.items():
        parts = platform.split('|')
        godot_platform = parts[0]
        mono_platform = parts[-1]

        if target_platform and target_platform != mono_platform:
            continue

        for arch in archs:
            parts = arch.split('|')
            godot_arch = parts[0]
            mono_arch = parts[-1]

            if target_arch and target_arch != mono_arch:
                continue

            platform = Platform(godot_platform, mono_platform)
            arch = Arch(godot_arch, mono_arch)
            yield Target(platform, arch)

            if target_arch:
                break

        if target_platform:
            break

import sys, platform
current_arch = 'x86_64' if platform.machine().endswith('64') else 'x86'
current_platform = 'windows' if sys.platform in ('cygwin', 'msys') or platform.release().endswith('WSL2') else sys.platform

def get_current_target():
    [first, *rest] = yield_export_targets(current_platform, current_arch)
    assert(first and not rest)
    return first
