from config import *

godot_remote = 'https://github.com/godotengine/godot.git'
godot_local = '.build.src/godot'
godot_bin = '.build.bin/godot'

godot_build_tools_remote = 'https://github.com/godotengine/godot-mono-builds.git'
godot_build_tools_local = '.build.src/godot-build-tools'

mono_remote = 'https://github.com/mono/mono.git'
mono_local = f'.build.src/{mono_version}'
mono_bin = f'.build.bin/{mono_version}'
mono_cfg = f'.build.cfg/{mono_version}'

emscripten_remote = 'https://github.com/emscripten-core/emsdk.git'
emscripten_local = f'.build.src/emscripten-{emscripten_version}'

mxe_remote = 'https://github.com/mxe/mxe.git'
mxe_local = '.build.src/mxe'

if godot_version:
    godot_local += f'-{godot_version}'
    godot_bin += f'-{godot_version}'

editor_bin = f'{godot_bin}/Editor'
export_bin = f'{godot_bin}/Export'
editor_profile = 'editor_profile.py'
export_profile = 'export_profile.py'

import sys
mxe_root = f'{mxe_local}/usr'
mxe_path = f'{mxe_local}/usr/bin'
mxe_required = sys.platform == 'linux' # Includes wsl/linux, excludes cygwin/msys :)

patch_path = '.patches'
