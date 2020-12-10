<# .SYNOPSIS #>
[CmdletBinding()]
Param([ValidateSet('Away', 'Display', 'System')]$Mode = 'System')

################################################################################
### Functions ##################################################################
################################################################################

function Caffeinate {
    $SetThreadExecutionState = @'
[DllImport("Kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
public static extern void SetThreadExecutionState(uint esFlags);
'@
    $ES_CONTINUOUS = [uint32]'0x80000000'

    $mode = switch($Mode) {
        Away    { [uint32]'0x00000040' }
        Display { [uint32]'0x00000002' }
        System  { [uint32]'0x00000001' }
    }

    $caffeinate = Add-Type -MemberDefinition $SetThreadExecutionState `
                           -Namespace Win32 `
                           -Name System `
                           -PassThru
    $caffeinate::SetThreadExecutionState($ES_CONTINUOUS -bor $mode)
}

################################################################################
### MAIN #######################################################################
################################################################################

Caffeinate
