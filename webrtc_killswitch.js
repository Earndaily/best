/**
 * The Infiltrator - WebRTC Kill-Switch
 * Prevents WebRTC STUN/TURN leaks that expose local network IP addresses
 * 
 * Injection Method: Use with Playwright's page.addInitScript()
 */

/**
 * Complete WebRTC blocking approach
 * This script must be injected BEFORE any page scripts load
 */
(function() {
    'use strict';
    
    // Log WebRTC protection status
    const logProtection = (message) => {
        console.log(`[WebRTC Protection] ${message}`);
    };
    
    // Method 1: Complete RTCPeerConnection override
    if (window.RTCPeerConnection) {
        const OriginalRTCPeerConnection = window.RTCPeerConnection;
        
        window.RTCPeerConnection = function(configuration, constraints) {
            logProtection('RTCPeerConnection blocked - preventing STUN leak');
            
            // Block by returning a neutered object
            return {
                createOffer: () => Promise.reject(new Error('WebRTC disabled for security')),
                createAnswer: () => Promise.reject(new Error('WebRTC disabled for security')),
                setLocalDescription: () => Promise.reject(new Error('WebRTC disabled for security')),
                setRemoteDescription: () => Promise.reject(new Error('WebRTC disabled for security')),
                addIceCandidate: () => Promise.reject(new Error('WebRTC disabled for security')),
                getConfiguration: () => ({}),
                getStats: () => Promise.resolve(new Map()),
                close: () => {},
                addEventListener: () => {},
                removeEventListener: () => {},
                dispatchEvent: () => false
            };
        };
        
        // Preserve prototype chain for compatibility
        window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
        
        logProtection('RTCPeerConnection overridden');
    }
    
    // Method 2: Block webkitRTCPeerConnection (Safari/older Chrome)
    if (window.webkitRTCPeerConnection) {
        window.webkitRTCPeerConnection = window.RTCPeerConnection;
        logProtection('webkitRTCPeerConnection overridden');
    }
    
    // Method 3: Block mozRTCPeerConnection (Firefox)
    if (window.mozRTCPeerConnection) {
        window.mozRTCPeerConnection = window.RTCPeerConnection;
        logProtection('mozRTCPeerConnection overridden');
    }
    
    // Method 4: Intercept getUserMedia to prevent media stream leaks
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
        
        navigator.mediaDevices.getUserMedia = function(constraints) {
            logProtection('getUserMedia blocked - preventing media leak');
            return Promise.reject(new DOMException('Permission denied', 'NotAllowedError'));
        };
    }
    
    // Legacy getUserMedia blocking
    if (navigator.getUserMedia) {
        navigator.getUserMedia = function(constraints, successCallback, errorCallback) {
            logProtection('Legacy getUserMedia blocked');
            if (errorCallback) {
                errorCallback(new DOMException('Permission denied', 'NotAllowedError'));
            }
        };
    }
    
    // Method 5: Block RTCDataChannel
    if (window.RTCDataChannel) {
        const OriginalRTCDataChannel = window.RTCDataChannel;
        window.RTCDataChannel = function() {
            logProtection('RTCDataChannel blocked');
            throw new Error('RTCDataChannel disabled for security');
        };
    }
    
    // Method 6: Block enumerateDevices (prevents device fingerprinting)
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
        
        navigator.mediaDevices.enumerateDevices = function() {
            logProtection('enumerateDevices spoofed - returning minimal device list');
            
            // Return minimal fake device list
            return Promise.resolve([
                {
                    deviceId: 'default',
                    kind: 'audioinput',
                    label: '',
                    groupId: 'default'
                },
                {
                    deviceId: 'default',
                    kind: 'audiooutput',
                    label: '',
                    groupId: 'default'
                },
                {
                    deviceId: 'default',
                    kind: 'videoinput',
                    label: '',
                    groupId: 'default'
                }
            ]);
        };
    }
    
    // Method 7: Freeze WebRTC configuration to prevent runtime changes
    Object.freeze(window.RTCPeerConnection);
    
    logProtection('WebRTC kill-switch activated - all leak vectors blocked');
    
})();


/**
 * Alternative: Minimal STUN server filtering approach
 * Use this if you need WebRTC functionality but want to prevent IP leaks
 */
(function() {
    'use strict';
    
    if (!window.RTCPeerConnection) return;
    
    const OriginalRTCPeerConnection = window.RTCPeerConnection;
    
    window.RTCPeerConnection = function(configuration, constraints) {
        // Filter out STUN/TURN servers from configuration
        if (configuration && configuration.iceServers) {
            configuration.iceServers = configuration.iceServers.filter(server => {
                const urls = Array.isArray(server.urls) ? server.urls : [server.urls];
                
                // Block STUN/TURN servers
                const hasStunTurn = urls.some(url => 
                    url.startsWith('stun:') || url.startsWith('turn:')
                );
                
                if (hasStunTurn) {
                    console.log('[WebRTC Protection] Blocked STUN/TURN server:', urls);
                    return false;
                }
                
                return true;
            });
            
            // If all servers were filtered, provide empty array
            if (configuration.iceServers.length === 0) {
                console.log('[WebRTC Protection] All ICE servers blocked - using empty configuration');
            }
        }
        
        return new OriginalRTCPeerConnection(configuration, constraints);
    };
    
    window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
    
    console.log('[WebRTC Protection] STUN/TURN filtering active');
    
})();


/**
 * Python usage example with Playwright
 */
const pythonUsageExample = `
from playwright.sync_api import sync_playwright

def inject_webrtc_protection(page):
    """Inject WebRTC protection before page load"""
    
    # Read the WebRTC kill-switch script
    with open('webrtc_killswitch.js', 'r') as f:
        webrtc_script = f.read()
    
    # Inject BEFORE navigating to the page
    page.add_init_script(webrtc_script)
    
    print("[+] WebRTC protection injected")

# Usage
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    
    # Inject protection
    inject_webrtc_protection(page)
    
    # Now navigate - WebRTC will be blocked
    page.goto('https://example.com')
`;
