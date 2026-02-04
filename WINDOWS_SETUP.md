# The Infiltrator - Windows Setup Guide

This guide will help you run The Infiltrator research framework on Windows without requiring Linux, while maintaining all functionality.

## Option 1: Docker Desktop (RECOMMENDED - Full Functionality)

This method preserves ALL features including network-layer manipulation (MAC/TTL).

### Prerequisites
1. **Windows 10/11 Pro, Enterprise, or Education** (required for Hyper-V)
2. **Docker Desktop for Windows**

### Step 1: Install Docker Desktop

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install Docker Desktop
3. During installation, ensure "Use WSL 2 instead of Hyper-V" is CHECKED
4. Restart your computer
5. Start Docker Desktop and wait for it to initialize

### Step 2: Build The Infiltrator Container

Open PowerShell or Command Prompt in your infiltrator folder:

```powershell
# Navigate to your infiltrator directory
cd C:\path\to\infiltrator

# Build the Docker image
docker build -t infiltrator:latest .

# Verify the image was created
docker images
```

### Step 3: Run The Infiltrator

```powershell
# Run with network privileges (for MAC/TTL manipulation)
docker run -it --cap-add=NET_ADMIN --privileged infiltrator:latest
```

**What happens:**
1. Interactive prompt asks for Target URL, Proxy, and User-Agent
2. System performs GeoIP lookup and timezone synchronization
3. Network masking applies MAC and TTL spoofing
4. Browser session starts with full protection

### Important Notes for Docker on Windows:
- Network layer features (MAC/TTL) work INSIDE the container
- The container has its own network stack isolated from Windows
- Proxy routing works normally
- All Python scripts function identically to Linux

---

## Option 2: Native Windows (Limited Network Features)

If you can't use Docker, you can run most features natively on Windows. **Note:** MAC/TTL manipulation won't work natively on Windows.

### Prerequisites

1. **Python 3.10+**
   - Download from: https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"

2. **Git for Windows** (optional, for easy updates)
   - Download from: https://git-scm.com/download/win

### Step 1: Install Python Dependencies

Open PowerShell or Command Prompt:

```powershell
# Navigate to infiltrator directory
cd C:\path\to\infiltrator

# Install required packages
pip install playwright==1.40.0 requests==2.31.0 python-socks[asyncio]

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium
```

### Step 2: Modify Network Script for Windows

Since `network_mask.sh` is a bash script, you have two options:

#### Option A: Skip Network Masking (Easiest)
The network masking is optional for basic testing. Comment it out in the code.

#### Option B: Use PowerShell Equivalent (See network_mask.ps1 below)

### Step 3: Run The Infiltrator

```powershell
# Run the entrypoint script
python entrypoint.py

# Or run the complete integration
python infiltrator_complete.py
```

---

## Option 3: WSL2 (Windows Subsystem for Linux) - Full Functionality

This gives you a real Linux environment inside Windows with ALL features working.

### Step 1: Install WSL2

Open PowerShell as Administrator:

```powershell
# Install WSL2
wsl --install

# Restart your computer

# After restart, check WSL is installed
wsl --list --verbose
```

### Step 2: Install Ubuntu in WSL

```powershell
# Install Ubuntu (default distribution)
wsl --install -d Ubuntu

# Launch Ubuntu
wsl
```

### Step 3: Setup Inside WSL

Now you're in Linux! Run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip git curl wget

# Install required packages
pip3 install playwright requests python-socks[asyncio]
playwright install chromium
playwright install-deps chromium

# Install network tools
sudo apt install -y iproute2 iptables faketime

# Navigate to your infiltrator folder
# Windows drives are mounted at /mnt/
cd /mnt/c/path/to/infiltrator

# Make scripts executable
chmod +x network_mask.sh
chmod +x identity_sync.py
chmod +x entrypoint.py

# Run the infiltrator
python3 entrypoint.py
```

**Accessing Windows Files from WSL:**
- C: drive → `/mnt/c/`
- D: drive → `/mnt/d/`
- Example: `C:\Users\YourName\Desktop\infiltrator` → `/mnt/c/Users/YourName/Desktop/infiltrator`

---

## Comparison of Options

| Feature | Docker Desktop | Native Windows | WSL2 |
|---------|---------------|----------------|------|
| MAC Spoofing | ✅ Yes | ❌ No | ✅ Yes |
| TTL Manipulation | ✅ Yes | ❌ No | ✅ Yes |
| Timezone Sync | ✅ Yes | ⚠️ Limited | ✅ Yes |
| libfaketime | ✅ Yes | ❌ No | ✅ Yes |
| WebRTC Protection | ✅ Yes | ✅ Yes | ✅ Yes |
| Mouse/Timing | ✅ Yes | ✅ Yes | ✅ Yes |
| Browser Automation | ✅ Yes | ✅ Yes | ✅ Yes |
| Setup Complexity | Medium | Easy | Medium |
| Performance | Good | Best | Good |

---

## Troubleshooting

### Docker Issues

**Problem:** "Docker daemon not running"
**Solution:** 
1. Open Docker Desktop application
2. Wait for it to fully start (icon turns solid)
3. Try command again

**Problem:** "Cannot connect to Docker daemon"
**Solution:**
```powershell
# Restart Docker Desktop
# Or in PowerShell as Admin:
Restart-Service docker
```

### Native Windows Issues

**Problem:** "playwright: command not found"
**Solution:**
```powershell
# Ensure Python Scripts folder is in PATH
python -m playwright install
```

**Problem:** Timezone not changing
**Solution:** 
Windows timezone requires admin privileges. Run PowerShell as Administrator:
```powershell
Set-TimeZone -Id "Eastern Standard Time"
```

### WSL Issues

**Problem:** "WSL 2 requires an update to its kernel component"
**Solution:**
Download and install: https://aka.ms/wsl2kernel

**Problem:** "This operation returned because the timeout period expired"
**Solution:**
```powershell
# Restart WSL
wsl --shutdown
wsl
```

---

## Testing Your Setup

After installation, test each component:

### 1. Test Python and Playwright
```powershell
python -c "import playwright; print('Playwright OK')"
```

### 2. Test GeoIP Lookup
```powershell
python identity_sync.py --proxy-ip 8.8.8.8 --os-type windows
```

### 3. Test Complete Flow
```powershell
python entrypoint.py
# Enter test values when prompted:
# URL: https://httpbin.org/headers
# Proxy: (leave blank or use test proxy)
# User-Agent: (select default)
```

---

## Recommended Setup for Research

For serious research work:

1. **For Development/Testing:** Native Windows (Option 2)
   - Fast, easy to debug
   - Good for testing behavioral components

2. **For Full Research:** Docker Desktop (Option 1) or WSL2 (Option 3)
   - Complete feature set
   - Network-layer manipulation
   - Production-ready

---

## Next Steps

After setup, you can:

1. **Run Interactive Bootstrap:**
   ```powershell
   python entrypoint.py
   ```

2. **Run Complete Integration:**
   ```powershell
   python infiltrator_complete.py
   ```

3. **Test Individual Components:**
   ```powershell
   python kinematic_mouse.py
   python temporal_entropy.py
   python reading_mimicry.py
   ```

---

## Security Notes

- This framework is for **research purposes only**
- Always use in a controlled environment
- Respect the terms of service of websites you visit
- Do not use for malicious purposes
- Proxy usage may be logged by your ISP

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify Python version: `python --version` (should be 3.10+)
4. Check Docker is running: `docker --version`

For Windows-specific issues with network components, Docker or WSL2 is required for full functionality.
