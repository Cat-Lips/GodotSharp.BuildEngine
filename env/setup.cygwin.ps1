<# .SYNOPSIS #>
[CmdletBinding()]
Param([string]$cmd)

. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$cygwin_root = Get-RootDir '.env.cygwin'
$cygwin_workspace = "$cygwin_root/root"

################################################################################
### Functions ##################################################################
################################################################################

function Setup {
    if (Test-Path $cygwin_root) { return }

    $cygwin_setup = "$cygwin_root/setup-x86_64.exe"
    $cygwin_remote = 'https://www.cygwin.com/setup-x86_64.exe'
    $cygwin_mirror = 'http://mirror.internode.on.net/pub/cygwin' # From https://cygwin.com/mirrors.html
    $cygwin_packages = "$cygwin_root/packages"
    $cygwin_args = "--no-admin --no-shortcuts --quiet-mode --root $(Get-AbsolutePath $cygwin_workspace) --local-package-dir $(Get-AbsolutePath $cygwin_packages) --site $cygwin_mirror"
    $cygwin_args += ' --packages autoconf,automake,bison,gcc-core,gcc-g++,mingw64-i686-runtime,mingw64-i686-binutils,mingw64-i686-gcc-core,mingw64-i686-gcc-g++,mingw64-i686-pthreads,mingw64-i686-w32api,mingw64-x86_64-runtime,mingw64-x86_64-binutils,mingw64-x86_64-gcc-core,mingw64-x86_64-gcc-g++,mingw64-x86_64-pthreads,mingw64-x86_64-w32api,libtool,make,python,gettext-devel,gettext,intltool,libiconv,pkg-config,git,curl,wget,libxslt,bc,patch,cmake,perl,yasm,unzip' # Mono
    $cygwin_args += ',libX11-devel,libXcursor-devel,libXinerama-devel,libXrandr-devel,libXi-devel' # Godot

    function Initialise {
        New-Item -Force $cygwin_root -ItemType Directory | Out-Null
    }

    function Download {
        if (Test-Path $cygwin_setup) { return }
        Write-Output 'Downloading Cygwin...'
        Invoke-WebRequest $cygwin_remote -OutFile $cygwin_setup
    }

    function Install {
        if (Test-Path $cygwin_packages) { return }
        Write-Output 'Installing Cygwin...'
        Start-Process -NoNewWindow -Wait $cygwin_setup $cygwin_args
    }

    function Setup {
        if (Test-Path $cygwin_workspace/home/*) { return }
        Write-Output 'Preparing Cygwin...'
        Execute "echo >> .bash_profile; echo cd $(Get-RootDir) >> .bash_profile"
        Execute 'python3 -m pip install humanize scons'
    }

    Initialise
    Download
    Install
    Setup
}

function Execute([string]$cmd) {
    $cygwin_cmd = "$cygwin_workspace/bin/bash"
    $cygwin_args = "--login -i -c '$cmd'"

    Write-Output "Executing: $cygwin_cmd $cygwin_args"
    Start-Process -NoNewWindow -Wait $cygwin_cmd $cygwin_args
}

################################################################################
### MAIN #######################################################################
################################################################################

Setup
Execute $cmd
