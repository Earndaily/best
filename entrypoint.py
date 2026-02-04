#!/usr/bin/env python3
"""
The Infiltrator - Interactive Bootstrap Entrypoint
Captures manual configuration and orchestrates the identity sync sequence
"""

import sys
import re
import socket
import urllib.parse
from typing import Dict, Optional, Tuple
import subprocess
import os


class ProxyValidator:
    """Validates and parses proxy configurations"""
    
    @staticmethod
    def parse_proxy(proxy_string: str) -> Dict[str, str]:
        """
        Parse proxy string into components
        Supports: socks5://user:pass@host:port or http://host:port
        """
        if not proxy_string:
            raise ValueError("Proxy string cannot be empty")
        
        # Add scheme if missing
        if not re.match(r'^(socks5|http|https)://', proxy_string):
            proxy_string = f'socks5://{proxy_string}'
        
        parsed = urllib.parse.urlparse(proxy_string)
        
        if not parsed.hostname:
            raise ValueError("Invalid proxy format. Use: protocol://[user:pass@]host:port")
        
        return {
            'protocol': parsed.scheme,
            'host': parsed.hostname,
            'port': parsed.port or (1080 if parsed.scheme == 'socks5' else 8080),
            'username': parsed.username,
            'password': parsed.password
        }
    
    @staticmethod
    def verify_connectivity(host: str, port: int, timeout: int = 5) -> bool:
        """Test TCP connectivity to proxy"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"[!] Connectivity test failed: {e}")
            return False


class InteractiveBootstrap:
    """Handles interactive configuration collection"""
    
    def __init__(self):
        self.config = {}
    
    def collect_target_url(self) -> str:
        """Prompt for and validate target URL"""
        while True:
            url = input("\n[*] Enter Target URL: ").strip()
            
            if not url:
                print("[!] URL cannot be empty")
                continue
            
            # Add scheme if missing
            if not re.match(r'^https?://', url):
                url = f'https://{url}'
            
            try:
                parsed = urllib.parse.urlparse(url)
                if not parsed.netloc:
                    print("[!] Invalid URL format")
                    continue
                print(f"[+] Target: {url}")
                return url
            except Exception as e:
                print(f"[!] URL parsing error: {e}")
    
    def collect_proxy(self) -> Dict[str, str]:
        """Prompt for and validate proxy configuration"""
        while True:
            proxy_input = input("\n[*] Enter Proxy (socks5://host:port or http://host:port): ").strip()
            
            try:
                proxy_config = ProxyValidator.parse_proxy(proxy_input)
                
                # Display parsed configuration
                print(f"\n[+] Proxy Configuration:")
                print(f"    Protocol: {proxy_config['protocol']}")
                print(f"    Host: {proxy_config['host']}")
                print(f"    Port: {proxy_config['port']}")
                if proxy_config['username']:
                    print(f"    Auth: {proxy_config['username']}:***")
                
                # Verify connectivity
                print(f"\n[*] Testing connectivity to {proxy_config['host']}:{proxy_config['port']}...")
                if ProxyValidator.verify_connectivity(proxy_config['host'], proxy_config['port']):
                    print("[+] Proxy is reachable")
                    return proxy_config
                else:
                    print("[!] Proxy is not reachable. Please verify and try again.")
                    retry = input("[?] Continue anyway? (y/n): ").strip().lower()
                    if retry == 'y':
                        return proxy_config
            
            except ValueError as e:
                print(f"[!] {e}")
    
    def collect_user_agent(self) -> str:
        """Prompt for User-Agent string"""
        print("\n[*] User-Agent Options:")
        print("    1. Chrome Windows (Default)")
        print("    2. Chrome macOS")
        print("    3. Chrome Linux")
        print("    4. Firefox Windows")
        print("    5. Safari macOS")
        print("    6. Chrome Android")
        print("    7. Safari iOS")
        print("    8. Custom")
        
        presets = {
            '1': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '2': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '3': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '4': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            '5': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            '6': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
            '7': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        }
        
        choice = input("\n[*] Select User-Agent (1-8, default=1): ").strip() or '1'
        
        if choice == '8':
            ua = input("[*] Enter custom User-Agent: ").strip()
            if not ua:
                print("[!] Using default Chrome Windows")
                ua = presets['1']
        else:
            ua = presets.get(choice, presets['1'])
        
        print(f"[+] User-Agent: {ua[:80]}...")
        return ua
    
    def detect_os_type(self, user_agent: str) -> str:
        """Detect OS type from User-Agent for TTL configuration"""
        ua_lower = user_agent.lower()
        
        if 'android' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower:
            return 'mobile'
        elif 'windows' in ua_lower:
            return 'windows'
        elif 'mac os' in ua_lower or 'darwin' in ua_lower:
            return 'macos'
        elif 'linux' in ua_lower:
            return 'linux'
        else:
            return 'windows'  # Default fallback
    
    def run(self) -> Dict:
        """Execute interactive bootstrap sequence"""
        print("=" * 60)
        print("THE INFILTRATOR - Research Automation Framework")
        print("=" * 60)
        
        # Collect configuration
        self.config['target_url'] = self.collect_target_url()
        self.config['proxy'] = self.collect_proxy()
        self.config['user_agent'] = self.collect_user_agent()
        self.config['os_type'] = self.detect_os_type(self.config['user_agent'])
        
        # Summary
        print("\n" + "=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)
        print(f"Target URL: {self.config['target_url']}")
        print(f"Proxy: {self.config['proxy']['protocol']}://{self.config['proxy']['host']}:{self.config['proxy']['port']}")
        print(f"Detected OS: {self.config['os_type'].upper()}")
        print(f"User-Agent: {self.config['user_agent'][:80]}...")
        print("=" * 60)
        
        confirm = input("\n[?] Proceed with this configuration? (y/n): ").strip().lower()
        if confirm != 'y':
            print("[!] Configuration cancelled. Exiting.")
            sys.exit(0)
        
        return self.config


def save_config(config: Dict, filepath: str = '/tmp/infiltrator_config.env'):
    """Save configuration to environment file for downstream scripts"""
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


def trigger_identity_sync(config: Dict):
    """Trigger the identity synchronization sequence"""
    print("\n[*] Initiating Identity Sync Sequence...")
    
    # Call the identity sync script
    proxy_ip = config['proxy']['host']
    os_type = config['os_type']
    
    try:
        subprocess.run([
            '/usr/local/bin/identity_sync.py',
            '--proxy-ip', proxy_ip,
            '--os-type', os_type
        ], check=True)
        print("[+] Identity Sync Complete")
    except subprocess.CalledProcessError as e:
        print(f"[!] Identity Sync failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("[!] Identity sync script not found. Continuing without sync...")


def main():
    """Main entrypoint orchestration"""
    try:
        # Run interactive bootstrap
        bootstrap = InteractiveBootstrap()
        config = bootstrap.run()
        
        # Save configuration for other scripts
        save_config(config)
        
        # Trigger identity synchronization
        trigger_identity_sync(config)
        
        print("\n[+] Bootstrap Complete - System Ready")
        print("[*] Configuration available at: /tmp/infiltrator_config.env")
        
    except KeyboardInterrupt:
        print("\n\n[!] Bootstrap interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
