#!/usr/bin/env python3
"""
The Infiltrator - Windows-Compatible Entrypoint
Cross-platform bootstrap that adapts to Windows or Linux environments
"""

import sys
import os
import platform
import subprocess
from entrypoint import InteractiveBootstrap, save_config

# Detect operating system
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'


def detect_environment():
    """Detect execution environment and available features"""
    env_info = {
        'platform': platform.system(),
        'is_windows': IS_WINDOWS,
        'is_linux': IS_LINUX,
        'is_docker': os.path.exists('/.dockerenv'),
        'is_wsl': 'microsoft' in platform.uname().release.lower() if IS_LINUX else False,
        'has_network_tools': False,
        'has_faketime': False
    }
    
    # Check for network manipulation tools
    if IS_LINUX:
        try:
            subprocess.run(['which', 'iptables'], capture_output=True, check=True)
            env_info['has_network_tools'] = True
        except:
            pass
        
        try:
            subprocess.run(['which', 'faketime'], capture_output=True, check=True)
            env_info['has_faketime'] = True
        except:
            pass
    
    return env_info


def print_environment_info(env_info):
    """Display environment capabilities"""
    print("\n" + "="*60)
    print("ENVIRONMENT DETECTION")
    print("="*60)
    print(f"Platform: {env_info['platform']}")
    
    if env_info['is_docker']:
        print("Environment: Docker Container ✓")
        print("Network Features: FULL (MAC/TTL manipulation available)")
    elif env_info['is_wsl']:
        print("Environment: WSL2 ✓")
        print("Network Features: FULL (with sudo privileges)")
    elif env_info['is_linux']:
        print("Environment: Native Linux")
        print(f"Network Features: {'FULL' if env_info['has_network_tools'] else 'LIMITED'}")
    elif env_info['is_windows']:
        print("Environment: Native Windows")
        print("Network Features: LIMITED (MAC/TTL not available)")
        print("")
        print("⚠️  For full functionality, consider using:")
        print("    1. Docker Desktop (recommended)")
        print("    2. WSL2")
        print("    See WINDOWS_SETUP.md for details")
    
    print("="*60)


def trigger_identity_sync_windows(config):
    """Windows-compatible identity synchronization"""
    print("\n[*] Initiating Identity Sync (Windows Mode)...")
    
    proxy_ip = config['proxy']['host']
    os_type = config['os_type']
    
    try:
        # Check if identity_sync.py exists
        if os.path.exists('identity_sync.py'):
            script_path = 'identity_sync.py'
        else:
            script_path = os.path.join(os.path.dirname(__file__), 'identity_sync.py')
        
        # Run with Python
        result = subprocess.run([
            sys.executable,
            script_path,
            '--proxy-ip', proxy_ip,
            '--os-type', os_type
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Identity Sync Complete")
            print(result.stdout)
        else:
            print(f"[!] Identity Sync completed with warnings:")
            print(result.stdout)
            print(result.stderr)
            print("[!] Continuing without full synchronization...")
    
    except Exception as e:
        print(f"[!] Identity Sync error: {e}")
        print("[!] Continuing without synchronization...")


def trigger_network_mask_windows(config):
    """Attempt Windows network masking (limited)"""
    print("\n[*] Network Layer Masking (Windows Mode)...")
    
    print("[!] Windows network masking has limitations:")
    print("    - MAC spoofing: Not recommended")
    print("    - TTL manipulation: Global registry changes")
    print("    - Requires Administrator privileges")
    print("")
    
    response = input("[?] Attempt Windows network masking? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            # Check for PowerShell script
            ps_script = 'network_mask.ps1'
            
            if not os.path.exists(ps_script):
                print("[!] network_mask.ps1 not found, skipping network masking")
                return
            
            # Run PowerShell script
            # Note: This requires running Python as Administrator
            cmd = [
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', ps_script,
                '-OsType', config['os_type']
            ]
            
            subprocess.run(cmd)
            
        except Exception as e:
            print(f"[!] Network masking failed: {e}")
            print("[!] Continuing without network masking...")
    else:
        print("[*] Skipping network masking")


def trigger_network_mask_linux(config):
    """Linux network masking"""
    print("\n[*] Network Layer Masking (Linux Mode)...")
    
    os_type = config['os_type']
    
    try:
        # Check for bash script
        script_path = 'network_mask.sh'
        
        if not os.path.exists(script_path):
            script_path = '/usr/local/bin/network_mask.sh'
        
        if not os.path.exists(script_path):
            print("[!] network_mask.sh not found")
            print("[!] Skipping network masking...")
            return
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Run with sudo if available
        if os.geteuid() == 0:
            # Already root
            cmd = [script_path, '--os-type', os_type]
        else:
            # Try with sudo
            cmd = ['sudo', script_path, '--os-type', os_type]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Network Masking Complete")
            print(result.stdout)
        else:
            print("[!] Network masking failed:")
            print(result.stderr)
            print("[!] Continuing without network masking...")
    
    except Exception as e:
        print(f"[!] Network masking error: {e}")
        print("[!] Continuing without network masking...")


def save_config_windows(config, filepath='infiltrator_config.env'):
    """Save configuration in current directory for Windows"""
    try:
        # On Windows, save to current directory
        if IS_WINDOWS:
            filepath = os.path.join(os.getcwd(), 'infiltrator_config.env')
        else:
            filepath = '/tmp/infiltrator_config.env'
        
        with open(filepath, 'w') as f:
            f.write(f"TARGET_URL={config['target_url']}\n")
            f.write(f"PROXY_PROTOCOL={config['proxy']['protocol']}\n")
            f.write(f"PROXY_HOST={config['proxy']['host']}\n")
            f.write(f"PROXY_PORT={config['proxy']['port']}\n")
            if config['proxy']['username']:
                f.write(f"PROXY_USERNAME={config['proxy']['username']}\n")
                f.write(f"PROXY_PASSWORD={config['proxy']['password']}\n")
            f.write(f"USER_AGENT={config['user_agent']}\n")
            f.write(f"OS_TYPE={config['os_type']}\n")
        
        print(f"[+] Configuration saved to {filepath}")
        return filepath
    
    except Exception as e:
        print(f"[!] Failed to save configuration: {e}")
        return None


def main():
    """Cross-platform main entrypoint"""
    
    # Detect environment
    env_info = detect_environment()
    
    print("=" * 60)
    print("THE INFILTRATOR - Cross-Platform Research Framework")
    print("=" * 60)
    
    # Display environment capabilities
    print_environment_info(env_info)
    
    try:
        # Run interactive bootstrap (same on all platforms)
        bootstrap = InteractiveBootstrap()
        config = bootstrap.run()
        
        # Save configuration (platform-aware)
        save_config_windows(config)
        
        # Platform-specific identity sync
        if IS_WINDOWS:
            trigger_identity_sync_windows(config)
        else:
            # Use original Linux version
            from entrypoint import trigger_identity_sync
            trigger_identity_sync(config)
        
        # Platform-specific network masking
        if IS_WINDOWS:
            trigger_network_mask_windows(config)
        elif IS_LINUX and env_info['has_network_tools']:
            trigger_network_mask_linux(config)
        else:
            print("\n[!] Network masking not available on this platform")
            print("    Install required tools or use Docker/WSL2")
        
        print("\n[+] Bootstrap Complete - System Ready")
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("Run the complete integration:")
        print(f"  {sys.executable} infiltrator_complete.py")
        print("")
        print("Or test individual components:")
        print(f"  {sys.executable} kinematic_mouse.py")
        print(f"  {sys.executable} temporal_entropy.py")
        print(f"  {sys.executable} reading_mimicry.py")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n[!] Bootstrap interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
