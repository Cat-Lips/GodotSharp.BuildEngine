<# .SYNOPSIS #>
[CmdletBinding()]
Param(
    [switch]$update # Update Godot repositories
   ,[switch]$editor # Build Godot Editor for current platform (windows)
   ,[switch]$export # Build export templates for all supported platforms (TODO)
   ,[switch]$mono   # Include C# support
   ,[ValidateSet('cygwin','msys','wsl')]
    $platform = 'cygwin' # Build using Cygwin (default), MSYS (todo), WSL (admin, sudo)
   ,[ValidateSet('dotnet','msbuild','msvc')]
    $build = 'dotnet' # Use DotNet (default), MSBuild (admin) to build additional Godot Editor components required for mono.  Can also specify MSVC to MSBuild all of Godot (reinstall, admin).
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

. $PSScriptRoot/Caffeinate.ps1 Display
. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$cmd = . {
    $cmd = 'build/main.py'
    if ($update) { $cmd += ' -update' }
    if ($editor) { $cmd += ' -editor' }
    if ($export) { $cmd += ' -export' }
    if ($mono) { $cmd += ' -mono' }
    return $cmd
}

################################################################################
### MAIN #######################################################################
################################################################################

if ($build -eq 'msvc') {
    & $PSScriptRoot/setup.msbuild.ps1 -cpp
} else {
    & $PSScriptRoot/setup.$build.ps1
}

& $PSScriptRoot/setup.$platform.ps1 $cmd
