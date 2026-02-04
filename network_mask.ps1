# The Infiltrator - Network Layer Masking (Windows PowerShell Version)
# Note: This provides limited functionality compared to Linux version
# For full MAC/TTL manipulation, use Docker or WSL2

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('mobile', 'windows', 'macos', 'linux')]
    [string]$OsType,
    
    [Parameter(Mandatory=$false)]
    [string]$MacAddress = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Interface = ""
)

# Color output functions
function Write-Info {
    param([string]$Message)
    Write-Host "[+] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Red
}

# TTL values based on OS fingerprinting
$TTL_VALUES = @{
    'mobile' = 64
    'linux' = 64
    'macos' = 64
    'windows' = 128
}

Write-Host "============================================================"
Write-Host "Network Layer Masking - Windows PowerShell Version"
Write-Host "============================================================"
Write-Host ""

# Check for Administrator privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Err "This script must be run as Administrator"
    Write-Warn "Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

# WARNING: Windows Limitations
Write-Warn "Windows Limitations:"
Write-Host "  - MAC address spoofing: Not recommended (may break connectivity)"
Write-Host "  - TTL manipulation: Not natively supported"
Write-Host "  - For full functionality, use Docker or WSL2"
Write-Host ""

$continue = Read-Host "Continue with limited functionality? (y/n)"
if ($continue -ne 'y') {
    Write-Info "Exiting. Consider using Docker or WSL2 for full features."
    exit 0
}

# Get network adapter
if ($Interface -eq "") {
    Write-Info "Detecting primary network adapter..."
    
    # Get active network adapter with internet connectivity
    $adapter = Get-NetAdapter | Where-Object {
        $_.Status -eq 'Up' -and $_.InterfaceDescription -notlike '*Loopback*'
    } | Select-Object -First 1
    
    if ($adapter) {
        $Interface = $adapter.Name
        Write-Info "Detected adapter: $Interface"
    } else {
        Write-Err "Could not detect active network adapter"
        exit 1
    }
}

# Display current configuration
Write-Info "Current Network Configuration:"
$currentAdapter = Get-NetAdapter -Name $Interface -ErrorAction SilentlyContinue
if ($currentAdapter) {
    $ipConfig = Get-NetIPAddress -InterfaceAlias $Interface -AddressFamily IPv4 -ErrorAction SilentlyContinue
    
    Write-Host "  Interface: $($currentAdapter.Name)"
    Write-Host "  Description: $($currentAdapter.InterfaceDescription)"
    Write-Host "  MAC Address: $($currentAdapter.MacAddress)"
    Write-Host "  Status: $($currentAdapter.Status)"
    
    if ($ipConfig) {
        Write-Host "  IP Address: $($ipConfig.IPAddress)"
    }
} else {
    Write-Err "Interface '$Interface' not found"
    exit 1
}

Write-Host ""

# TTL Configuration Note
Write-Info "TTL Configuration:"
$targetTTL = $TTL_VALUES[$OsType]
Write-Host "  Target OS: $OsType"
Write-Host "  Target TTL: $targetTTL"
Write-Warn "  Windows does not support TTL manipulation natively"
Write-Host "  Registry-based TTL changes affect ALL connections globally"
Write-Host ""

$modifyTTL = Read-Host "Modify global Windows TTL? (y/n - this affects all applications)"
if ($modifyTTL -eq 'y') {
    try {
        # Windows registry TTL modification
        # WARNING: This is GLOBAL and affects all network traffic
        
        $registryPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
        
        # Backup current value
        $currentTTL = Get-ItemProperty -Path $registryPath -Name "DefaultTTL" -ErrorAction SilentlyContinue
        
        if ($currentTTL) {
            Write-Info "Current TTL: $($currentTTL.DefaultTTL)"
            Write-Host "  Backing up to: C:\Windows\Temp\infiltrator_ttl_backup.txt"
            $currentTTL.DefaultTTL | Out-File "C:\Windows\Temp\infiltrator_ttl_backup.txt"
        }
        
        # Set new TTL
        Set-ItemProperty -Path $registryPath -Name "DefaultTTL" -Value $targetTTL -Type DWord
        
        Write-Info "TTL set to: $targetTTL"
        Write-Warn "Restart required for TTL changes to take effect"
        Write-Info "To restore original TTL later, run:"
        Write-Host "  Set-ItemProperty -Path '$registryPath' -Name 'DefaultTTL' -Value <original_value>"
        
    } catch {
        Write-Err "Failed to modify TTL: $_"
    }
}

# MAC Address Spoofing (NOT RECOMMENDED on Windows)
if ($MacAddress -ne "") {
    Write-Warn "MAC Address Spoofing on Windows"
    Write-Host "  Requested MAC: $MacAddress"
    Write-Err "  MAC spoofing is NOT recommended on Windows:"
    Write-Host "    - May break network connectivity"
    Write-Host "    - Driver-dependent (may not work)"
    Write-Host "    - Requires network adapter restart"
    Write-Host ""
    
    $confirmMAC = Read-Host "Are you SURE you want to proceed? (type YES to confirm)"
    
    if ($confirmMAC -eq "YES") {
        try {
            # Attempt to set MAC via registry (driver-dependent)
            $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            
            # Find the adapter's registry key
            $adapterGUID = $currentAdapter.InterfaceGuid
            
            # This is highly driver-dependent and may not work
            Write-Warn "Attempting MAC change (this may fail)..."
            
            # Most adapters require this format (no colons/dashes)
            $macFormatted = $MacAddress -replace '[:-]', ''
            
            Set-ItemProperty -Path "$regPath\000*" -Name "NetworkAddress" -Value $macFormatted -ErrorAction Stop
            
            # Restart adapter
            Restart-NetAdapter -Name $Interface
            
            Start-Sleep -Seconds 2
            
            $newAdapter = Get-NetAdapter -Name $Interface
            Write-Info "New MAC: $($newAdapter.MacAddress)"
            
        } catch {
            Write-Err "MAC spoofing failed: $_"
            Write-Info "This is expected on most Windows systems"
        }
    }
}

# Save configuration
$configFile = "C:\Windows\Temp\infiltrator_network_config.txt"
$config = @"
OS_TYPE=$OsType
TTL=$targetTTL
INTERFACE=$Interface
TIMESTAMP=$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
"@

$config | Out-File $configFile
Write-Info "Configuration saved to: $configFile"

Write-Host ""
Write-Host "============================================================"
Write-Info "Network Configuration Complete"
Write-Host "============================================================"
Write-Host ""
Write-Warn "Important Reminders:"
Write-Host "  1. TTL changes are GLOBAL and affect all applications"
Write-Host "  2. Restart may be required for changes to take effect"
Write-Host "  3. For research, Docker/WSL2 provide better isolation"
Write-Host "  4. Restore original settings after testing"
Write-Host ""

# Offer to create restore script
$createRestore = Read-Host "Create restore script? (y/n)"
if ($createRestore -eq 'y') {
    $restoreScript = @"
# Infiltrator - Network Restore Script
# Restores original network configuration

Write-Host "Restoring network configuration..."

# Restore TTL
`$registryPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
Remove-ItemProperty -Path `$registryPath -Name "DefaultTTL" -ErrorAction SilentlyContinue

Write-Host "[+] TTL restored to system default"
Write-Host "[!] Restart required for changes to take effect"

# Restore MAC (if modified)
`$regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
Remove-ItemProperty -Path "`$regPath\000*" -Name "NetworkAddress" -ErrorAction SilentlyContinue

Write-Host "[+] MAC address restored to hardware default"
Write-Host "[!] Restart network adapter:"
Write-Host "    Restart-NetAdapter -Name '$Interface'"

Write-Host ""
Write-Host "Restoration complete. Please restart your computer."
"@
    
    $restoreScript | Out-File "restore_network.ps1"
    Write-Info "Restore script created: restore_network.ps1"
    Write-Host "  Run with: .\restore_network.ps1 (as Administrator)"
}

Write-Host ""
