# 🚀 QUICK START - Windows Users

## ⚡ Fastest Method (5 Minutes)

### 1. Install Python
- Download: https://www.python.org/downloads/
- ✅ Check "Add Python to PATH"

### 2. Install Dependencies
```cmd
cd C:\path\to\infiltrator
pip install -r requirements.txt
playwright install chromium
```

### 3. Run
```cmd
START_WINDOWS.bat
```

**Done!** Follow the prompts.

---

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `START_WINDOWS.bat` | **Double-click to run** - Easy launcher |
| `entrypoint_windows.py` | Main Windows entrypoint |
| `infiltrator_complete.py` | Complete browsing mission |
| `kinematic_mouse.py` | Human-like mouse movement |
| `temporal_entropy.py` | Realistic timing delays |
| `reading_mimicry.py` | Natural reading behavior |
| `identity_sync.py` | GeoIP + timezone sync |
| `webrtc_killswitch.js` | Blocks IP leaks |
| `network_mask.ps1` | Windows network config (optional) |
| `Dockerfile` | For Docker users |

---

## 💡 Three Ways to Run

### Option 1: Easy Mode ⭐
```cmd
START_WINDOWS.bat
```
Interactive menu guides you.

### Option 2: Command Line
```cmd
python entrypoint_windows.py
```
Full control, same experience.

### Option 3: Docker (Full Features)
```powershell
docker build -t infiltrator .
docker run -it --cap-add=NET_ADMIN --privileged infiltrator
```
Includes MAC/TTL spoofing.

---

## 🔍 What Happens When You Run

```
1. System detects your environment (Windows/Linux/Docker)
2. Prompts for:
   - Target URL
   - Proxy (optional)
   - User-Agent
3. Performs GeoIP lookup on proxy
4. Syncs timezone
5. Launches browser with protections
6. Executes human-like browsing
```

---

## ✅ Feature Checklist

**Working on Windows (Native):**
- ✅ Proxy routing (SOCKS5/HTTP)
- ✅ WebRTC blocking
- ✅ Kinematic mouse
- ✅ Gaussian timing
- ✅ Honeypot detection
- ✅ Reading simulation

**Requires Docker/WSL2:**
- 🐳 MAC address spoofing
- 🐳 TTL manipulation
- 🐳 libfaketime

---

## 🆘 Common Issues

**"Python not found"**
→ Reinstall Python, check "Add to PATH"

**"playwright not found"**
→ Run: `pip install playwright && playwright install chromium`

**"Module not found"**
→ Run: `pip install -r requirements.txt`

**Browser won't start**
→ Run: `playwright install chromium`

---

## 📖 Documentation

- **README_WINDOWS.md** - Complete Windows guide
- **WINDOWS_SETUP.md** - Detailed setup instructions
- **Dockerfile** - For Docker users

---

## 🎓 Example Run

```cmd
> START_WINDOWS.bat

[Select] 1. Run Full Infiltrator

[*] Enter Target URL: https://example.com
[*] Enter Proxy: (press Enter to skip)
[*] Select User-Agent: 1

[+] Configuration complete
[+] GeoIP lookup: New York, US
[+] Timezone synced
[+] Browser launching...
[+] Mission executing...
```

---

## ⚠️ Important

- **Research use only**
- Test in controlled environments
- Respect Terms of Service
- Use responsibly

---

## 🎉 You're Ready!

Just run:
```cmd
START_WINDOWS.bat
```

Or:
```cmd
python entrypoint_windows.py
```

Happy researching! 🔬
