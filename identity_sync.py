#!/usr/bin/env python3
"""
The Infiltrator - Dynamic Identity Sync (The "Perfect Lie")
Synchronizes container identity with proxy geolocation
"""

import argparse
import subprocess
import os
import sys
import json
import random
from typing import Dict, Optional
import urllib.request
import urllib.error


class GeoIPLookup:
    """Handles geolocation lookup for proxy IP"""
    
    # Multiple fallback APIs for reliability
    APIS = [
        'http://ip-api.com/json/{ip}',
        'https://ipapi.co/{ip}/json/',
        'http://www.geoplugin.net/json.gp?ip={ip}'
    ]
    
    @staticmethod
    def lookup(ip: str) -> Optional[Dict]:
        """
        Query multiple GeoIP APIs until one succeeds
        Returns: dict with timezone, city, country, lat, lon
        """
        print(f"[*] Performing GeoIP lookup for {ip}...")
        
        for api_url in GeoIPLookup.APIS:
            try:
                url = api_url.format(ip=ip)
                print(f"    Trying: {url}")
                
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    
                    # Normalize different API response formats
                    result = GeoIPLookup._normalize_response(data, api_url)
                    
                    if result and result.get('timezone'):
                        print(f"[+] GeoIP Success: {result['city']}, {result['country']} (TZ: {result['timezone']})")
                        return result
                    
            except Exception as e:
                print(f"    Failed: {e}")
                continue
        
        print("[!] All GeoIP APIs failed")
        return None
    
    @staticmethod
    def _normalize_response(data: Dict, api_url: str) -> Dict:
        """Normalize different API response formats"""
        if 'ip-api.com' in api_url:
            return {
                'timezone': data.get('timezone'),
                'city': data.get('city'),
                'country': data.get('country'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon')
            }
        elif 'ipapi.co' in api_url:
            return {
                'timezone': data.get('timezone'),
                'city': data.get('city'),
                'country': data.get('country_name'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude')
            }
        elif 'geoplugin.net' in api_url:
            return {
                'timezone': data.get('geoplugin_timezone'),
                'city': data.get('geoplugin_city'),
                'country': data.get('geoplugin_countryName'),
                'latitude': data.get('geoplugin_latitude'),
                'longitude': data.get('geoplugin_longitude')
            }
        return {}


class TimezoneSync:
    """Handles system timezone synchronization"""
    
    @staticmethod
    def set_timezone(timezone: str) -> bool:
        """
        Set container timezone via /etc/localtime and TZ variable
        Returns: True if successful
        """
        print(f"\n[*] Setting timezone to: {timezone}")
        
        try:
            # Method 1: Link to zoneinfo
            zoneinfo_path = f'/usr/share/zoneinfo/{timezone}'
            
            if not os.path.exists(zoneinfo_path):
                print(f"[!] Timezone file not found: {zoneinfo_path}")
                return False
            
            # Remove existing localtime
            if os.path.exists('/etc/localtime'):
                os.remove('/etc/localtime')
            
            # Create symlink
            os.symlink(zoneinfo_path, '/etc/localtime')
            print(f"[+] Linked /etc/localtime -> {zoneinfo_path}")
            
            # Method 2: Set TZ environment variable
            os.environ['TZ'] = timezone
            
            # Persist to /etc/environment for all processes
            with open('/etc/environment', 'a') as f:
                f.write(f'\nTZ={timezone}\n')
            
            print(f"[+] Set TZ environment variable: {timezone}")
            
            # Method 3: Update /etc/timezone (Debian/Ubuntu)
            with open('/etc/timezone', 'w') as f:
                f.write(f'{timezone}\n')
            
            print(f"[+] Updated /etc/timezone")
            
            return True
            
        except Exception as e:
            print(f"[!] Timezone sync failed: {e}")
            return False


class LibFakeTime:
    """Integrates libfaketime for clock drift simulation"""
    
    @staticmethod
    def generate_drift(seconds_range: int = 5) -> int:
        """
        Generate random clock drift (±N seconds)
        Simulates "human clock drift" - clocks slightly out of sync
        """
        # Gaussian distribution centered at 0, with range as std dev
        drift = int(random.gauss(0, seconds_range / 2))
        # Clamp to ±range
        drift = max(-seconds_range, min(seconds_range, drift))
        return drift
    
    @staticmethod
    def configure(drift_seconds: int = None) -> bool:
        """
        Configure libfaketime for the container
        Creates faketime configuration for process-level time manipulation
        """
        if drift_seconds is None:
            drift_seconds = LibFakeTime.generate_drift()
        
        print(f"\n[*] Configuring libfaketime with {drift_seconds:+d}s drift...")
        
        try:
            # Check if libfaketime is installed
            result = subprocess.run(['which', 'faketime'], capture_output=True)
            if result.returncode != 0:
                print("[!] libfaketime not installed. Installing...")
                subprocess.run(['apt-get', 'update', '-qq'], check=True)
                subprocess.run(['apt-get', 'install', '-y', '-qq', 'faketime'], check=True)
            
            # Create faketime wrapper script
            wrapper_path = '/usr/local/bin/faketime_wrapper.sh'
            
            # Determine offset format (e.g., "+3s" or "-2s")
            offset = f"{drift_seconds:+d}s"
            
            wrapper_content = f"""#!/bin/bash
# libfaketime wrapper - Human Clock Drift Simulation
# Offset: {offset}
export FAKETIME="{offset}"
export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1"
exec "$@"
"""
            
            with open(wrapper_path, 'w') as f:
                f.write(wrapper_content)
            
            os.chmod(wrapper_path, 0o755)
            
            print(f"[+] libfaketime configured: {offset} drift")
            print(f"[+] Wrapper created: {wrapper_path}")
            
            # Create environment variable for easy access
            with open('/etc/environment', 'a') as f:
                f.write(f'FAKETIME={offset}\n')
                f.write(f'LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1\n')
            
            return True
            
        except Exception as e:
            print(f"[!] libfaketime configuration failed: {e}")
            return False
    
    @staticmethod
    def test_drift():
        """Test that faketime is working correctly"""
        try:
            result = subprocess.run(
                ['faketime', '+5s', 'date'],
                capture_output=True,
                text=True
            )
            print(f"\n[*] Faketime Test:")
            print(f"    Real time: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
            print(f"    Fake time (+5s): {result.stdout.strip()}")
        except Exception as e:
            print(f"[!] Faketime test failed: {e}")


class IdentitySync:
    """Main orchestrator for identity synchronization"""
    
    def __init__(self, proxy_ip: str, os_type: str):
        self.proxy_ip = proxy_ip
        self.os_type = os_type
        self.geo_data = None
    
    def execute(self) -> bool:
        """Execute full identity sync sequence"""
        print("=" * 60)
        print("IDENTITY SYNC SEQUENCE - The Perfect Lie")
        print("=" * 60)
        
        # Step 1: GeoIP Lookup
        self.geo_data = GeoIPLookup.lookup(self.proxy_ip)
        
        if not self.geo_data:
            print("\n[!] WARNING: GeoIP lookup failed. Using fallback timezone.")
            self.geo_data = {
                'timezone': 'UTC',
                'city': 'Unknown',
                'country': 'Unknown'
            }
        
        # Step 2: Timezone Synchronization
        if not TimezoneSync.set_timezone(self.geo_data['timezone']):
            print("[!] Timezone sync failed - continuing with system default")
        
        # Step 3: libfaketime Configuration
        if not LibFakeTime.configure():
            print("[!] libfaketime setup failed - clock drift disabled")
        else:
            LibFakeTime.test_drift()
        
        # Save synchronized identity
        self._save_identity()
        
        print("\n" + "=" * 60)
        print("[+] IDENTITY SYNC COMPLETE")
        print("=" * 60)
        print(f"Location: {self.geo_data['city']}, {self.geo_data['country']}")
        print(f"Timezone: {self.geo_data['timezone']}")
        print(f"OS Type: {self.os_type}")
        print("=" * 60)
        
        return True
    
    def _save_identity(self):
        """Save identity configuration for other components"""
        identity_file = '/tmp/infiltrator_identity.json'
        
        identity = {
            'proxy_ip': self.proxy_ip,
            'timezone': self.geo_data['timezone'],
            'city': self.geo_data['city'],
            'country': self.geo_data['country'],
            'latitude': self.geo_data.get('latitude'),
            'longitude': self.geo_data.get('longitude'),
            'os_type': self.os_type
        }
        
        with open(identity_file, 'w') as f:
            json.dump(identity, f, indent=2)
        
        print(f"\n[+] Identity saved to: {identity_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Dynamic Identity Sync - Synchronize container with proxy geolocation'
    )
    parser.add_argument('--proxy-ip', required=True, help='Proxy IP address for GeoIP lookup')
    parser.add_argument('--os-type', required=True, choices=['mobile', 'windows', 'macos', 'linux'],
                        help='Operating system type for TTL configuration')
    
    args = parser.parse_args()
    
    try:
        syncer = IdentitySync(args.proxy_ip, args.os_type)
        success = syncer.execute()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
