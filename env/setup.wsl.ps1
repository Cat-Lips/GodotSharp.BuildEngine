<# .SYNOPSIS #>
[CmdletBinding()]
Param([string]$cmd)

. $PSScriptRoot/utils.ps1

################################################################################
### Constants ##################################################################
################################################################################

$wsl_root = Get-RootDir '.env.wsl'
$wsl_exe = "$wsl_root/ubuntu1604.exe"
if ($SecureSetupRequired) { return !(Test-Path $wsl_root) }

################################################################################
### Functions ##################################################################
################################################################################

function Setup {
    function Activate-WSL {
        Run-Elevated {
            Write-Output '* Activating WSL...'

            $vm_enabled = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform # (Requires admin)
            $wsl_enabled = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux # (Requires admin)

            if ($vm_enabled -and $wsl_enabled) {
                Write-Output ' - WSL already active'
                return
            }

            Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux,VirtualMachinePlatform -All -NoRestart # (Requires admin)
            Write-Output ' - WSL activated'
        }
    }

    function Update-WSL {
        $wsl_update_remote = 'https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi'
        $wsl_update_installer = "$wsl_root/wsl_update_x64.msi"

        Write-Output '* Downloading WSL Update...'
        New-Item -Force $wsl_root -ItemType Directory | Out-Null
        Invoke-WebRequest $wsl_update_remote -OutFile $wsl_update_installer

        Write-Output '* Installing WSL Update...'
        Write-Output "Executing: $wsl_update_installer /q"
        Start-Process -NoNewWindow -Wait $wsl_update_installer /q

        wsl --set-default-version 2

        Remove-Item -Force $wsl_update_installer
    }

    function Install-Ubuntu1604 {
        $wsl_distribution_remote = 'https://aka.ms/wsl-ubuntu-1604'
        $wsl_distribution_package = "$wsl_root/ubuntu1604.zip"

        if ($(wsl -l -q | Out-String).Contains('Ubuntu 16.04')) {
            Write-Warning 'Updating existing installation...'
        }

        Write-Output '* Downloading WSL Distribution (Ubuntu 16.04)...'
        Invoke-WebRequest $wsl_distribution_remote -OutFile $wsl_distribution_package

        Write-Output '* Unpacking WSL Distribution...'
        Expand-Archive $wsl_distribution_package $wsl_root
        Remove-Item -Force $wsl_distribution_package

        $wsl_args = 'install --root'
        Write-Output '* Installing WSL Distribution...'
        Write-Output "Executing: $wsl_exe $wsl_args"
        Start-Process -NoNewWindow -Wait $wsl_exe $wsl_args
    }

    function Initialise-Ubuntu1604 {
        Write-Output '* Initialising WSL Distribution...'
        Execute "sudo -H env/setup.wsl.sh" # (Requires manual password entry)
    }

    if (!(Test-Path $wsl_root)) {
        Activate-WSL
        Update-WSL
    }

    if (!(Test-Path $wsl_cmd)) {
        Install-Ubuntu1604
        Initialise-Ubuntu1604
    }
}

function Execute([string]$cmd) {
    $wsl_args = "run $cmd"
    Write-Output "Executing: $wsl_exe $wsl_args"
    Start-Process -NoNewWindow -Wait $wsl_exe $wsl_args
}

################################################################################
### MAIN #######################################################################
################################################################################

Setup
Execute $cmd
