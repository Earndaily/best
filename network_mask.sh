#!/bin/bash
#
# The Infiltrator - Network Layer Masking
# MAC Address Spoofing + TTL Manipulation
#
# Usage: ./network_mask.sh --os-type [mobile|windows|macos|linux] [--mac-address XX:XX:XX:XX:XX:XX]
#

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
OS_TYPE=""
CUSTOM_MAC=""
INTERFACE="eth0"

# TTL values based on OS fingerprinting
declare -A TTL_VALUES=(
    ["mobile"]="64"      # Android/iOS
    ["linux"]="64"       # Linux
    ["macos"]="64"       # macOS
    ["windows"]="128"    # Windows
)

# Function: Print colored output
log_info() {
    echo -e "${GREEN}[+]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[!]${NC} $1"
}

# Function: Generate random MAC address
generate_mac() {
    local oui_prefix="00:16:3e"  # Common Xen/KVM prefix (looks legitimate)
    local random_suffix=$(openssl rand -hex 3 | sed 's/\(..\)/\1:/g; s/:$//')
    echo "${oui_prefix}:${random_suffix}"
}

# Function: Validate MAC address format
validate_mac() {
    local mac=$1
    if [[ $mac =~ ^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function: Set MAC address
set_mac_address() {
    local mac=$1
    local interface=$2
    
    log_info "Setting MAC address: ${mac} on ${interface}"
    
    # Bring interface down
    ip link set dev "${interface}" down
    
    # Set new MAC address
    ip link set dev "${interface}" address "${mac}"
    
    # Bring interface back up
    ip link set dev "${interface}" up
    
    # Verify the change
    local current_mac=$(ip link show "${interface}" | awk '/link\/ether/ {print $2}')
    
    if [ "${current_mac}" == "${mac}" ]; then
        log_info "MAC address successfully set to: ${current_mac}"
        return 0
    else
        log_error "MAC address verification failed"
        return 1
    fi
}

# Function: Configure TTL via iptables
set_ttl_value() {
    local ttl=$1
    
    log_info "Configuring TTL mangle: ${ttl}"
    
    # Clear existing mangle rules
    iptables -t mangle -F
    
    # Add TTL mangling rule for all outgoing packets
    iptables -t mangle -A POSTROUTING -j TTL --ttl-set "${ttl}"
    
    # Verify rule was added
    local rule_count=$(iptables -t mangle -L POSTROUTING -n | grep -c "TTL set to ${ttl}" || true)
    
    if [ "${rule_count}" -gt 0 ]; then
        log_info "TTL mangling rule added successfully"
        
        # Display current rules
        log_info "Current mangle table:"
        iptables -t mangle -L POSTROUTING -n -v | grep -E "TTL|Chain" | sed 's/^/    /'
        
        return 0
    else
        log_error "Failed to add TTL mangling rule"
        return 1
    fi
}

# Function: Get primary network interface
get_primary_interface() {
    # Find the interface with a default route
    local iface=$(ip route | grep default | awk '{print $5}' | head -n1)
    
    if [ -z "${iface}" ]; then
        # Fallback: find first non-loopback interface
        iface=$(ip link show | awk -F: '/^[0-9]+: [^lo]/ {print $2; exit}' | tr -d ' ')
    fi
    
    echo "${iface}"
}

# Function: Display network configuration
display_config() {
    log_info "Current Network Configuration:"
    
    local iface="${INTERFACE}"
    
    # MAC Address
    local mac=$(ip link show "${iface}" | awk '/link\/ether/ {print $2}')
    echo "    Interface: ${iface}"
    echo "    MAC Address: ${mac}"
    
    # IP Address
    local ip=$(ip addr show "${iface}" | awk '/inet / {print $2}' | cut -d'/' -f1)
    echo "    IP Address: ${ip}"
    
    # TTL Rules
    echo "    TTL Mangle Rules:"
    iptables -t mangle -L POSTROUTING -n | grep TTL | sed 's/^/        /' || echo "        None"
}

# Function: Save configuration
save_config() {
    local config_file="/tmp/network_mask_config.txt"
    
    {
        echo "OS_TYPE=${OS_TYPE}"
        echo "TTL=${TTL_VALUES[$OS_TYPE]}"
        echo "MAC_ADDRESS=$(ip link show "${INTERFACE}" | awk '/link\/ether/ {print $2}')"
        echo "INTERFACE=${INTERFACE}"
        echo "TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "${config_file}"
    
    log_info "Configuration saved to: ${config_file}"
}

# Function: Restore original network configuration (cleanup)
restore_network() {
    log_warn "Restoring network configuration..."
    
    # Clear TTL rules
    iptables -t mangle -F
    
    log_info "Network restoration complete"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --os-type)
            OS_TYPE="$2"
            shift 2
            ;;
        --mac-address)
            CUSTOM_MAC="$2"
            shift 2
            ;;
        --interface)
            INTERFACE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 --os-type [mobile|windows|macos|linux] [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --os-type TYPE          Operating system type for TTL fingerprinting (required)"
            echo "  --mac-address MAC       Custom MAC address (optional, random if not specified)"
            echo "  --interface IFACE       Network interface (default: auto-detect)"
            echo "  --help                  Display this help message"
            echo ""
            echo "TTL Values:"
            echo "  Mobile (Android/iOS): 64"
            echo "  Linux: 64"
            echo "  macOS: 64"
            echo "  Windows: 128"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "============================================================"
    echo "Network Layer Masking - MAC + TTL Manipulation"
    echo "============================================================"
    
    # Validate OS type
    if [ -z "${OS_TYPE}" ]; then
        log_error "OS type is required. Use --os-type [mobile|windows|macos|linux]"
        exit 1
    fi
    
    if [ -z "${TTL_VALUES[$OS_TYPE]}" ]; then
        log_error "Invalid OS type: ${OS_TYPE}"
        exit 1
    fi
    
    # Check for root privileges
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Auto-detect interface if not specified
    if [ "${INTERFACE}" == "eth0" ]; then
        DETECTED_INTERFACE=$(get_primary_interface)
        if [ -n "${DETECTED_INTERFACE}" ]; then
            INTERFACE="${DETECTED_INTERFACE}"
            log_info "Auto-detected interface: ${INTERFACE}"
        fi
    fi
    
    # Verify interface exists
    if ! ip link show "${INTERFACE}" &> /dev/null; then
        log_error "Interface ${INTERFACE} does not exist"
        exit 1
    fi
    
    # Generate or validate MAC address
    if [ -z "${CUSTOM_MAC}" ]; then
        CUSTOM_MAC=$(generate_mac)
        log_info "Generated random MAC: ${CUSTOM_MAC}"
    else
        if ! validate_mac "${CUSTOM_MAC}"; then
            log_error "Invalid MAC address format: ${CUSTOM_MAC}"
            exit 1
        fi
        log_info "Using custom MAC: ${CUSTOM_MAC}"
    fi
    
    # Execute network masking
    echo ""
    log_info "Step 1: MAC Address Spoofing"
    if ! set_mac_address "${CUSTOM_MAC}" "${INTERFACE}"; then
        log_error "MAC spoofing failed"
        exit 1
    fi
    
    echo ""
    log_info "Step 2: TTL Manipulation"
    if ! set_ttl_value "${TTL_VALUES[$OS_TYPE]}"; then
        log_error "TTL manipulation failed"
        exit 1
    fi
    
    # Display final configuration
    echo ""
    echo "============================================================"
    display_config
    echo "============================================================"
    
    # Save configuration
    save_config
    
    echo ""
    log_info "Network masking complete - OS fingerprint: ${OS_TYPE^^}"
    
    # Setup cleanup trap
    trap restore_network EXIT INT TERM
}

# Execute main function
main
