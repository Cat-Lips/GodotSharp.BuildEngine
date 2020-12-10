import os
import re
import glob
import shlex
import platform
import subprocess
import multiprocessing

cores = multiprocessing.cpu_count()

def execute(cmd, wd=None, *, check=True, shell=False, pipe=False):
    print(f'Executing: {cmd}')
    result = subprocess.run(cmd if shell else shlex.split(cmd), cwd=wd, check=check, shell=shell, stdout=PIPE if pipe else None, stderr=STDOUT if pipe else None, text=True if pipe else False)
    return result.stdout if pipe else result.returncode

def get_git(git_remote, git_local, git_branch=None, *, submodules=False):
    if submodules: submodules = f'--recurse-submodules --shallow-submodules -j {cores}'
    if os.path.exists(git_local):
        grep = 'grep "Already up to date"'
        git_pull = f'git pull --deepen 1 --no-rebase --no-tags'
        if submodules: git_pull += f' {submodules}'
        updated = execute(f'{git_pull} | {grep}', git_local, check=False, shell=True)
        return 'updated' if updated else None
    else:
        git_clone = f'git clone --depth 1'
        if git_branch: git_clone += f' -b {git_branch} -c advice.detachedHead=false'
        if submodules: git_clone += f' {submodules}'
        execute(f'{git_clone} {git_remote} {git_local}')
        return 'cloned'

def apply_patch(patch, git_local):
    execute(f'git apply {os.path.relpath(patch, git_local)}', git_local)

def repo_name(git_remote, git_branch=None):
    repo_name = re.sub('\.git$', '', os.path.basename(git_remote))
    return f'{repo_name} ({git_branch or "master"})'

def find_path(search_pattern):
    return max(glob.glob(search_pattern), key=os.path.getmtime, default=None)
