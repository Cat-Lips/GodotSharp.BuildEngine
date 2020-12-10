<# .SYNOPSIS #>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$env_cygwin = Get-RootDir '.env.cygwin'
$env_msys = Get-RootDir '.env.msys'
$env_wsl = Get-RootDir '.env.wsl'
$src_root = '.build.src'
$patch_root = '.patches'

################################################################################
### Functions ##################################################################
################################################################################

function Generate-Patches {

    function Generate-Patches($platform) {

        function Generate-Patch($dir) {
            & "$PSScriptRoot/setup.$platform.ps1" "cd $src_root/$dir; git diff > ../../$patch_root/$dir.diff"
        }

        Generate-Patch godot
        Generate-Patch godot-build-tools
    }

    if (Test-Path $env_cygwin) { Generate-Patches 'cygwin' }
    elseif (Test-Path $env_msys) { Generate-Patches 'msys' }
    elseif (Test-Path $env_wsl) { Generate-Patches 'wsl' }
    else { Write-Error "No platform to diff ($env_cygwin|$env_msys|$env_wsl)" }
}

function Show-Error($error) {
    ($error | Out-String).Trim() | Write-Host `
        -Foreground $Host.PrivateData.ErrorForegroundColor `
        -Background $Host.PrivateData.ErrorBackgroundColor
}

function Cmd-Pause {
    cmd /c pause
}

################################################################################
### MAIN #######################################################################
################################################################################

try { Generate-Patches }
catch { Show-Error $_ }
finally { Cmd-Pause }
