# The Infiltrator - Windows User Guide

## 🚀 Quick Start for Windows Users

You have **3 options** to run The Infiltrator on Windows, each with different levels of functionality:

| Method | Functionality | Setup Time | Recommended For |
|--------|--------------|------------|-----------------|
| **🐳 Docker Desktop** | ⭐⭐⭐⭐⭐ Full | 15 min | Serious research |
| **🪟 Native Windows** | ⭐⭐⭐ Core features | 5 min | Quick testing |
| **🐧 WSL2** | ⭐⭐⭐⭐⭐ Full | 20 min | Development |

---

## Option 1: 🐳 Docker Desktop (RECOMMENDED)

### Why Docker?
- ✅ **Full functionality** - All features work exactly as designed
- ✅ **Easy cleanup** - Delete container when done
- ✅ **Isolated** - No changes to your Windows system
- ✅ **Network manipulation** - MAC/TTL spoofing works

### Installation Steps

#### Step 1: Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop/
2. Run installer
3. **Important:** Enable "Use WSL 2 based engine"
4. Restart computer
5. Launch Docker Desktop (wait for it to fully start)

#### Step 2: Build and Run

Open PowerShell or Command Prompt in your `infiltrator` folder:

```powershell
# Navigate to folder
cd C:\path\to\infiltrator

# Build the image (one time only)
docker build -t infiltrator:latest .

# Run the infiltrator
docker run -it --cap-add=NET_ADMIN --privileged infiltrator:latest
```

**That's it!** The interactive bootstrap will guide you through the rest.

#### What Happens Next?

```
1. Container starts
2. You're prompted for:
   - Target URL (e.g., https://example.com)
   - Proxy (optional, format: socks5://host:port)
   - User-Agent (choose from presets)
3. System performs GeoIP lookup
4. Timezone automatically syncs
5. Network masking activates
6. Browser launches with protections
7. Mission executes
```

### Docker Tips

**View Running Containers:**
```powershell
docker ps
```

**Stop Container:**
```powershell
docker stop <container-id>
```

**Remove Container:**
```powershell
docker rm <container-id>
```

**Remove Image (cleanup):**
```powershell
docker rmi infiltrator:latest
```

---

## Option 2: 🪟 Native Windows (Easiest)

### Why Native?
- ✅ **Fast** - No container overhead
- ✅ **Simple** - Just Python, no Docker
- ⚠️ **Limited** - No MAC/TTL manipulation

### Installation Steps

#### Step 1: Install Python

1. Download Python 3.10+ from: https://www.python.org/downloads/
2. **CRITICAL:** Check "Add Python to PATH" during installation
3. Verify: Open Command Prompt and type:
   ```
   python --version
   ```

#### Step 2: Install Dependencies

Open Command Prompt or PowerShell in your `infiltrator` folder:

```powershell
# Install Python packages
pip install playwright requests python-socks[asyncio]

# Install Playwright browser
playwright install chromium
```

#### Step 3: Run The Infiltrator

**Option A: Easy Mode (Batch File)**
```powershell
# Just double-click:
START_WINDOWS.bat
```

**Option B: Command Line**
```powershell
# Run the Windows-compatible entrypoint
python entrypoint_windows.py

# Or run complete integration
python infiltrator_complete.py
```

### What Works on Native Windows?

✅ **Working:**
- Proxy routing (SOCKS5/HTTP)
- WebRTC protection
- Kinematic mouse movement
- Temporal entropy (Gaussian timing)
- Reading mimicry
- Honeypot detection
- Browser automation

❌ **Not Available:**
- MAC address spoofing
- TTL manipulation
- libfaketime (clock drift)

**For full features → Use Docker or WSL2**

---

## Option 3: 🐧 WSL2 (Advanced)

### Why WSL2?
- ✅ **Full functionality** - Real Linux environment
- ✅ **Development-friendly** - Best for coding
- ✅ **Permanent** - Stays installed unlike Docker

### Installation Steps

#### Step 1: Install WSL2

Open PowerShell **as Administrator**:

```powershell
# Install WSL2
wsl --install

# Restart computer
```

After restart:

```powershell
# Verify installation
wsl --list --verbose
```

#### Step 2: Setup Ubuntu in WSL

WSL should open Ubuntu automatically. If not:
```powershell
wsl
```

Inside Ubuntu (you'll see a Linux terminal):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git curl wget iproute2 iptables faketime

# Install Python packages
pip3 install playwright requests python-socks[asyncio]

# Install Playwright
playwright install chromium
playwright install-deps chromium
```

#### Step 3: Access Your Files

Windows drives are mounted in WSL at `/mnt/`:

```bash
# Example: Navigate to Desktop
cd /mnt/c/Users/YourName/Desktop/infiltrator

# Make scripts executable
chmod +x network_mask.sh
chmod +x identity_sync.py
chmod +x entrypoint.py

# Run the infiltrator
python3 entrypoint.py
```

### WSL2 Tips

**Exit WSL:**
```bash
exit
```

**Restart WSL from Windows:**
```powershell
wsl --shutdown
wsl
```

**Copy files to/from WSL:**
- From Windows Explorer: `\\wsl$\Ubuntu\home\yourusername`
- From WSL: `/mnt/c/` = your C: drive

---

## 🎯 Step-by-Step: First Run (Native Windows)

### 1. Download All Files

Make sure you have these files in one folder:

```
infiltrator/
├── entrypoint.py
├── entrypoint_windows.py     ← Windows version
├── identity_sync.py
├── network_mask.sh            ← Linux only
├── network_mask.ps1           ← Windows version
├── webrtc_killswitch.js
├── kinematic_mouse.py
├── temporal_entropy.py
├── reading_mimicry.py
├── infiltrator_complete.py
├── START_WINDOWS.bat          ← Easy launcher
├── Dockerfile                 ← For Docker
└── WINDOWS_SETUP.md          ← This guide
```

### 2. Install Python

1. https://www.python.org/downloads/
2. Check "Add Python to PATH"
3. Install

### 3. Install Dependencies

Open Command Prompt in the `infiltrator` folder:

```cmd
pip install playwright requests python-socks[asyncio]
playwright install chromium
```

### 4. Run!

**Easy way:**
```cmd
START_WINDOWS.bat
```

**Or manually:**
```cmd
python entrypoint_windows.py
```

### 5. Follow Prompts

```
Enter Target URL: https://example.com
Enter Proxy: socks5://proxy.example.com:1080  (or press Enter to skip)
Select User-Agent: 1 (Chrome Windows)
```

### 6. Watch It Work

The system will:
1. Validate your proxy
2. Lookup proxy geolocation
3. Configure timezone
4. Launch browser with protections
5. Navigate to target
6. Execute browsing behaviors

---

## 🔧 Troubleshooting

### "Python is not recognized"

**Problem:** Python not in PATH

**Solution:**
1. Reinstall Python
2. Check "Add Python to PATH"
3. OR manually add: `C:\Users\YourName\AppData\Local\Programs\Python\Python310`

### "playwright: command not found"

**Problem:** Playwright not installed properly

**Solution:**
```cmd
pip install playwright
python -m playwright install chromium
```

### "ModuleNotFoundError: No module named 'playwright'"

**Problem:** Dependencies not installed

**Solution:**
```cmd
cd C:\path\to\infiltrator
pip install playwright requests python-socks[asyncio]
```

### Browser doesn't launch

**Problem:** Playwright browsers not installed

**Solution:**
```cmd
playwright install chromium
playwright install-deps chromium
```

### "This script must be run as Administrator" (for network_mask.ps1)

**Problem:** PowerShell doesn't have admin rights

**Solution:**
1. Right-click PowerShell
2. "Run as Administrator"
3. Run script again

### Docker: "Docker daemon is not running"

**Problem:** Docker Desktop not started

**Solution:**
1. Launch Docker Desktop app
2. Wait for icon to turn solid
3. Try command again

---

## 📊 Feature Comparison

| Feature | Docker | Native Windows | WSL2 |
|---------|--------|----------------|------|
| **Core Functionality** |
| Proxy routing | ✅ | ✅ | ✅ |
| WebRTC blocking | ✅ | ✅ | ✅ |
| Mouse kinematics | ✅ | ✅ | ✅ |
| Gaussian timing | ✅ | ✅ | ✅ |
| Honeypot detection | ✅ | ✅ | ✅ |
| Reading mimicry | ✅ | ✅ | ✅ |
| **Advanced Features** |
| MAC spoofing | ✅ | ❌ | ✅ |
| TTL manipulation | ✅ | ⚠️ Global | ✅ |
| libfaketime | ✅ | ❌ | ✅ |
| Timezone sync | ✅ Full | ⚠️ Limited | ✅ Full |
| **Convenience** |
| Setup time | 15 min | 5 min | 20 min |
| Cleanup | Easy | Manual | Permanent |
| Isolation | Perfect | None | Good |

---

## 🎓 Usage Examples

### Example 1: Test with httpbin.org

```cmd
python entrypoint_windows.py

# When prompted:
Target URL: https://httpbin.org/headers
Proxy: (leave blank)
User-Agent: 1 (Chrome Windows)
```

This will show you all the headers the browser sends, useful for verification.

### Example 2: Use a SOCKS5 Proxy

```cmd
python entrypoint_windows.py

# When prompted:
Target URL: https://example.com
Proxy: socks5://your-proxy.com:1080
User-Agent: 6 (Chrome Android)
```

### Example 3: Run Individual Components

```cmd
# Test timing delays
python temporal_entropy.py

# Test mouse movements (demo)
python kinematic_mouse.py
```

---

## 📝 Important Notes

### For Native Windows Users

1. **Network Masking** is limited:
   - TTL changes are **GLOBAL** (affects all programs)
   - MAC spoofing **not recommended** (breaks connectivity)
   - For isolation, use Docker

2. **Administrator Privileges** needed for:
   - PowerShell network script
   - System-wide TTL changes

3. **Restore Original Settings** after testing:
   ```powershell
   .\restore_network.ps1  # Created by network_mask.ps1
   ```

### For All Users

- This is a **research framework**
- Use **responsibly** and **ethically**
- Respect website Terms of Service
- Do not use for malicious purposes
- Test in controlled environments only

---

## 🆘 Getting Help

1. **Read WINDOWS_SETUP.md** (detailed setup guide)
2. **Check Troubleshooting** section above
3. **Verify Python version:** `python --version` (must be 3.10+)
4. **Check dependencies:** `pip list | findstr playwright`
5. **Test Docker:** `docker --version`

---

## 🎉 You're Ready!

Choose your method:

- **Want full features?** → Docker Desktop
- **Want quick testing?** → Native Windows
- **Want to develop?** → WSL2

Then run:

```cmd
START_WINDOWS.bat
```

Or manually:

```cmd
python entrypoint_windows.py
```

Happy researching! 🔬
