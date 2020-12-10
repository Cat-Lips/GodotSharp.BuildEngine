<# .SYNOPSIS #>
[CmdletBinding()]
Param()

. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$dotnet_root = Get-RootDir '.env.dotnet'

################################################################################
### Functions ##################################################################
################################################################################

function Setup {
    if (Test-Path $dotnet_root) { return }
	if ($env:PATH -Match 'MSBuild|dotnet') { return }

    $dotnet_setup = "$dotnet_root/dotnet-install.ps1"
    $dotnet_remote = 'https://dot.net/v1/dotnet-install.ps1'
    $install_args = "-InstallDir $dotnet_root -Channel Current -NoPath"

    Write-Output 'Installing .NET...'
    New-Item -Force $dotnet_root -ItemType Directory | Out-Null
    Invoke-WebRequest $dotnet_remote -OutFile $dotnet_setup

    Write-Output "Executing: $dotnet_setup $install_args"
    Invoke-Expression "$dotnet_setup $install_args"
    Remove-Item -Force $dotnet_setup
}

################################################################################
### MAIN #######################################################################
################################################################################

Setup
SetEnv-Path $dotnet_root
