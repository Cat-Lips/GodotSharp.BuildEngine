<# .SYNOPSIS #>
[CmdletBinding()]
Param()

. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$msbuild_tmp = Get-RootDir '.tmp.msbuild'
$msbuild_root = Get-RootDir '.env.msbuild'

################################################################################
### Functions ##################################################################
################################################################################

function Setup {
    if (Test-Path $msbuild_root) { return }
	if ($env:PATH -Match 'MSBuild|dotnet') { return }

    $msbuild_setup = "$msbuild_tmp/vs_BuildTools.exe"
    $msbuild_remote = 'https://aka.ms/vs/16/release/vs_buildtools.exe'
    $install_args = "--passive --norestart --wait --nickname GodotSharp --installPath $(Get-AbsolutePath $msbuild_root)"
    $install_args += ' --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Component.NuGet.BuildTools'
    if ($cpp) { $install_args += ' --add Microsoft.VisualStudio.Workload.VCTools' }

    function Download {
        if (Test-Path $msbuild_root/MSBuild) { return }
        if (Test-Path $msbuild_setup) { return }

        Write-Output 'Downloading MSBuild...'
        New-Item -Force $msbuild_tmp -ItemType Directory | Out-Null
        Invoke-WebRequest $msbuild_remote -OutFile $msbuild_setup
    }

    function Install {
        if (Test-Path $msbuild_root/MSBuild) { return }

        Write-Output 'Installing MSBuild...'
        New-Item -Force $msbuild_root -ItemType Directory | Out-Null
        Start-Process -Wait -NoNewWindow $msbuild_setup $install_args # (Invokes elevation)
        Remove-Item -Force -Recurse $msbuild_tmp
    }

    Download
    Install
}

################################################################################
### MAIN #######################################################################
################################################################################

Setup
SetEnv-Path $msbuild_root/MSBuild/Current/Bin
