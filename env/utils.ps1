# Returns $dir in repo root as relative path from current dir
# Returns repo root as absolute path if $dir has no value
function Get-RootDir($dir) {
    if ($dir) {
        # Resolve-Path -Relative seems to always append ..\repo_root
        $repo_root = ((Split-Path $PSScriptRoot | Resolve-Path -Relative).Replace('\', '/').Split('/') | Select -SkipLast 2) -Join '/'
        if ($repo_root) { return "$repo_root/$dir" } else { return $dir }
    }

    return ([string](Split-Path $PSScriptRoot)).Replace('\', '/')
}

function Get-AbsolutePath([string]$path) {
    $path = Resolve-Path $path -ErrorAction SilentlyContinue -ErrorVariable err
    if (!$path) { $path = $err[0].TargetObject }
    return $path
}

function SetEnv-Path($path) {
    $env:PATH = (Get-AbsolutePath $path), $env:PATH -join [IO.Path]::PathSeparator
}

#function Run-Elevated($cmd) {
#    Write-Output "Executing (elevated): $cmd"
#    $p = Start-Process powershell $cmd -Verb RunAs -PassThru -Wait
#    if ($p.ExitCode) { Write-Error "Elevated Execution Failed [$cmd]" }
#}

#function Elevate-Process($root_invocation) {
#    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
#    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
#    $admin = [Security.Principal.WindowsBuiltInRole]::Administrator
#
#    if (!$principal.IsInRole($admin)) {
#        $args = "cd $(Get-Location);$($root_invocation.Line)"
#        Write-Output "Elevating Process [Executing (as admin): powershell $args]"
#        Start-Process powershell $args -Verb RunAs
#        exit
#    }
#}
