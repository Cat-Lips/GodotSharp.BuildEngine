import os
import utils
import shutil
from constants import *
from decorators import perf, title, scoped_env
from export_targets import get_current_target, yield_export_targets

class GodotBuilder:
    @perf('Total Runtime')
    def run(self, args):
        self.init(args)
        self.build(args)

    @perf('Total Init Time')
    def init(self, args):

        @title(f'Retrieving {utils.repo_name(godot_remote, godot_version)}')
        def get_godot():
            update_state = utils.get_git(godot_remote, godot_local, godot_version)
            if update_state == 'cloned':
                utils.apply_patch(f'{patch_path}/godot.diff', godot_local)
            elif update_state == 'updated':
                mono_glue_generator = utils.find_path(f'{godot_local}/bin/glue.*')
                if mono_glue_generator: os.remove(mono_glue_generator)

        @title(f'Retrieving {utils.repo_name(godot_build_tools_remote)}')
        def get_godot_build_tools():
            update_state = utils.get_git(godot_build_tools_remote, godot_build_tools_local)
            if update_state == 'cloned':
                utils.apply_patch(f'{patch_path}/godot-build-tools.diff', godot_build_tools_local)
            elif update_state == 'updated':
                print(f'WARNING: {godot_build_tools_remote} has been modified')
                print(' - Check if changes require rebuild or config.py version update')
                print('Meanwhile, continuing with current build...')

        @title(f'Retrieving {utils.repo_name(mono_remote, mono_version)}')
        def get_and_patch_mono():
            update_state = utils.get_git(mono_remote, mono_local, mono_version, submodules=True)
            if update_state == 'cloned':
                print('\nApplying Godot Patches...')
                utils.execute(f'{godot_build_tools_local}/patch_mono.py --mono-sources {mono_local}')

        @title(f'Retrieving {utils.repo_name(emscripten_remote, emscripten_version)}')
        def get_and_patch_emscripten():
            update_state = utils.get_git(emscripten_remote, emscripten_local)
            if update_state == 'cloned':
                print('\nApplying Godot Patches...')
                utils.execute(f'{godot_build_tools_local}/patch_emscripten.py --mono-sources {mono_local}')
            utils.execute(f'./emsdk install {emscripten_version}', emscripten_local)
            utils.execute(f'./emsdk activate {emscripten_version}', emscripten_local)

        def get_and_build_mxe():

            @title(f'Retrieving {utils.repo_name(mxe_remote)}')
            def get_mxe():
                utils.get_git(mxe_remote, mxe_local)

            @title(f'Building mxe')
            def build_mxe():
                mxe_plugins = 'MXE_PLUGIN_DIRS="plugins/gcc10"'
                mxe_targets = 'MXE_TARGETS="x86_64-w64-mingw32 i686-w64-mingw32"'
                utils.execute(f'make -j{utils.cores} --jobs={utils.cores} cc {mxe_targets} {mxe_plugins}', mxe_local)

            get_mxe()
            build_mxe()

        mono_required = args.mono
        emscripten_required = args.export
        godot_build_tools_required = mono_required or emscripten_required

        if args.update or not os.path.exists(godot_local): get_godot()
        if godot_build_tools_required and (args.update or not os.path.exists(godot_build_tools_local)): get_godot_build_tools()
        if emscripten_required and not os.path.exists(emscripten_local): get_and_patch_emscripten()
        if mono_required and not os.path.exists(mono_local): get_and_patch_mono()
        if mxe_required and not os.path.exists(mxe_root): get_and_build_mxe()

    @perf('Total Build Time')
    def build(self, args):

        def build(target, *, export=False):
            mono_arch = target.arch.mono
            godot_arch = target.arch.godot
            mono_platform = target.platform.mono
            godot_platform = target.platform.godot

            def mono_configure_dir():
                return f'{mono_cfg}/{mono_platform}.{mono_arch}'

            def mono_install_dir():
                return f'{mono_bin}/{mono_platform}.{mono_arch}'

            def mono_prefix_path():
                return utils.find_path(f'{mono_install_dir()}/*-{mono_arch}-*')

            def mono_glue_generator():
                return utils.find_path(f'{godot_local}/bin/glue.{godot_platform}.*')

            def godot_build_target():
                return utils.find_path(f'{godot_local}/bin/godot.{godot_platform}.*')

            @perf(f'Total Mono Build Time ({mono_platform}.{mono_arch})')
            def build_mono():
                install_dir = mono_install_dir()
                if os.path.exists(install_dir): return
                configure_dir = mono_configure_dir()

                product = 'desktop' if mono_platform in ['windows', 'linux', 'osx'] else mono_platform
                if mono_platform == 'windows' and mono_arch == 'x86': product += '-win32'

                bcl_cmd = f'python3 {godot_build_tools_local}/bcl.py'
                mono_cmd = f'python3 {godot_build_tools_local}/{mono_platform}.py'
                install_cmd = f'python3 {godot_build_tools_local}/reference_assemblies.py'
                base_args = f'-j{utils.cores} --configure-dir {configure_dir} --install-dir {install_dir} --mono-sources {mono_local}'
                if mxe_required: base_args += f' --mxe-prefix {mxe_root}'
                mono_args = f'{base_args} --target={mono_arch}'
                bcl_args = f'{base_args} --product={product}'

                @title(f'Configuring Mono ({mono_platform}.{mono_arch})')
                def configure_mono():
                    utils.execute(f'{mono_cmd} configure {mono_args}')

                @title(f'Compiling Mono ({mono_platform}.{mono_arch})')
                def compile_mono():
                    utils.execute(f'{mono_cmd} make {mono_args}')

                @title(f'Compiling BCL ({mono_platform}.{mono_arch})')
                def compile_bcl():
                    utils.execute(f'{bcl_cmd} make {bcl_args}')

                @title(f'Copying BCL ({mono_platform}.{mono_arch})')
                def copy_bcl():
                    utils.execute(f'{mono_cmd} copy-bcl {mono_args}')

                @title(f'Installing Mono ({mono_platform}.{mono_arch})')
                def install_mono():
                    utils.execute(f'{install_cmd} install {base_args}')

                configure_mono()
                compile_mono()
                compile_bcl()
                copy_bcl()
                install_mono()

            @perf(f'Total Mono Glue Generation Time')
            def generate_mono_glue():

                @title('Generating Mono Glue')
                def run_mono_glue_generator():
                    utils.execute(f'{mono_glue_generator()} --generate-mono-glue {godot_local}/modules/mono/glue --no-window')
                    os.remove('logs/godot.log')
                    os.rmdir('logs')

                if not mono_glue_generator():
                    build_godot(mono_glue=True)
                    run_mono_glue_generator()

            @perf(f'Total Godot Build Time ({godot_platform}.{mono_arch})')
            def build_godot(*, mono_glue=False):
                build_type = 'Mono Glue Generator' if mono_glue else 'Godot'

                def platform_args():
                    return f'platform={godot_platform} {godot_arch}'
                def profile_args():
                    profile_py = export_profile if export else editor_profile
                    return f' profile={profile_py}' if os.path.exists(profile_py) else ''
                def mono_args():
                    mono_glue_arg = 'mono_glue=no' if mono_glue else 'copy_mono_root=yes'
                    return f' module_mono_enabled=yes mono_static=yes {mono_glue_arg} mono_prefix={os.path.abspath(mono_prefix_path())}' if args.mono else ''
                def export_args():
                    return ' tools=no target=release debug_symbols=no use_lto=yes' if export else ' target=release_debug'

                scons_args = f'{platform_args()}{profile_args()}{mono_args()}{export_args()}'

                @scoped_env('PATH', mxe_path if mxe_required else None)
                @title(f'Building {build_type} ({godot_platform}.{mono_arch})')
                def build():
                    utils.execute(f'scons -j{utils.cores} --directory {godot_local} {scons_args}')

                @perf('(post-build)')
                def post_build():
                    godot_exe = godot_build_target()
                    if mono_glue:
                        mono_glue_exe = godot_exe.replace('godot.', 'glue.', 1)
                        utils.execute(f'mv {godot_exe} {mono_glue_exe}')
                    elif export:
                        os.makedirs(export_bin, exist_ok=True)
                        utils.execute(f'mv {godot_exe} {export_bin}')
                    else:
                        target_dir = f'{editor_bin}/{godot_platform}.{mono_arch}'
                        rollback_dir = f'{target_dir}.rollback'
                        if os.path.exists(rollback_dir):
                            print('Removing rollback...')
                            utils.execute(f'rm -rf {rollback_dir}')
                        if os.path.exists(target_dir):
                            print('Creating rollback...')
                            utils.execute(f'mv {target_dir} {rollback_dir}')
                        print('Moving build to bin...')
                        os.makedirs(target_dir)
                        utils.execute(f'mv {godot_exe} {target_dir}')
                        if args.mono: utils.execute(f'mv {godot_local}/bin/GodotSharp {target_dir}')
                        open(f'{target_dir}/_sc_', 'a').close()
                        editor_data = f'{rollback_dir}/editor_data'
                        if os.path.exists(editor_data): shutil.copytree(editor_data, f'{target_dir}/editor_data')

                build()
                post_build()

            if args.mono:
                build_mono()
                generate_mono_glue()
            build_godot()

        if args.editor:
            build(get_current_target())
        if args.export:
            [build(export_target, export=True) for export_target in yield_export_targets()]
