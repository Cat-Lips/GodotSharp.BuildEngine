import shlex
import subprocess

def execute(cmd):
    print(f'Executing: {cmd}')
    subprocess.run(shlex.split(cmd))
