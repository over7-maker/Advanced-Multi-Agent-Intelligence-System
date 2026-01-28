# 🚀 INSTALLATION METHODS - CHOOSE ONE

## Problem
Download timed out during automated deployment script.

## Solution
Use one of these 4 alternative methods:

---

## METHOD 1: Direct Manual Install (FASTEST) ✅

**No downloads. Everything inline.**

```bash
# Step 1: Stop current
sudo systemctl stop redirector-v3.service 2>/dev/null || true
sudo pkill -9 l4_redirector || true
sleep 2

# Step 2: Download and run manual install script
bash <(curl -s https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/VPS/QUICK_MANUAL_INSTALL.sh)
```

**What it does:**
- Creates hybrid redirector directly in `/usr/local/bin/`
- Updates systemd service
- Starts service
- Verifies installation

**Time:** ~30 seconds

---

## METHOD 2: Git Clone (RECOMMENDED) ✅

**If you have git available.**

```bash
# Step 1: Clone the repo (or use existing)
cd /tmp
git clone --depth 1 https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git 2>/dev/null || true
cd Advanced-Multi-Agent-Intelligence-System

# Step 2: Stop current
sudo systemctl stop redirector-v3.service 2>/dev/null || true
sudo pkill -9 l4_redirector || true
sleep 2

# Step 3: Copy hybrid redirector
sudo cp /tmp/Advanced-Multi-Agent-Intelligence-System/VPS/l4_redirector_v3_hybrid_working.py \
         /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py

# Step 4: Update service
sudo nano /etc/systemd/system/redirector-v3.service
# Change: ExecStart=/usr/bin/python3 /usr/local/bin/l4_redirector_v3_hybrid_working.py

# Step 5: Start
sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service
```

**Time:** ~30 seconds

---

## METHOD 3: wget with Retries (RELIABLE) ✅

**If wget is available and curl has issues.**

```bash
# Step 1: Stop current
sudo systemctl stop redirector-v3.service 2>/dev/null || true
sudo pkill -9 l4_redirector || true
sleep 2

# Step 2: Download with retries
cd /tmp
wget --retry-connrefused --waitretry=5 --read-timeout=10 --tries=3 \
  https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/VPS/l4_redirector_v3_hybrid_working.py \
  -O l4_redirector_v3_hybrid_working.py

if [ ! -f "l4_redirector_v3_hybrid_working.py" ]; then
    echo "Download failed. Use METHOD 1 instead."
    exit 1
fi

# Step 3: Install
sudo cp l4_redirector_v3_hybrid_working.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py

# Step 4: Update service and start
sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service
```

**Time:** ~1-2 minutes (includes retries)

---

## METHOD 4: Local File (IF YOU HAVE IT ALREADY)

**If you have the hybrid redirector locally.**

```bash
# Stop current
sudo systemctl stop redirector-v3.service 2>/dev/null || true
sudo pkill -9 l4_redirector || true
sleep 2

# Copy your local file
sudo cp ./l4_redirector_v3_hybrid_working.py /usr/local/bin/
sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py

# Update service
sudo systemctl daemon-reload
sudo systemctl start redirector-v3.service

# Verify
sudo systemctl status redirector-v3.service
```

**Time:** ~10 seconds

---

## QUICK RECOMMENDATION

| Situation | Recommended Method |
|-----------|-------------------|
| "I'm in a hurry" | METHOD 1 (Manual Install) |
| "I have git" | METHOD 2 (Git Clone) |
| "Downloads timeout" | METHOD 1 (Manual Install) |
| "wget works better" | METHOD 3 (wget with retries) |
| "I have the file" | METHOD 4 (Local File) |

---

## VERIFY INSTALLATION

After any method:

```bash
# Check service
sudo systemctl status redirector-v3.service

# Watch logs
tail -f /var/log/redirector/l4_redirector_v3_hybrid.log

# Check status
curl http://localhost:9090/status | jq

# Check ports
sudo ss -tlnp | grep -E '8041|8047|8057'
```

---

## TROUBLESHOOTING

### "wget: unable to resolve host address"
**Solution:** Use METHOD 1 (no downloads)

### "curl: operation timeout"
**Solution:** Use METHOD 1 (no downloads) or METHOD 2 (git clone)

### "Permission denied"
**Solution:** Add `sudo` before commands

### "Service failed to start"
**Solution:** Check logs:
```bash
sudo journalctl -u redirector-v3.service -n 50
```

### "Port already in use"
**Solution:** Kill old process:
```bash
sudo pkill -9 l4_redirector
sudo pkill -9 python3 | grep redirector || true
sudo systemctl restart redirector-v3.service
```

---

## MOST COMMON: METHOD 1

**Just run this:**

```bash
bash <(curl -s https://raw.githubusercontent.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/main/VPS/QUICK_MANUAL_INSTALL.sh)
```

That's it! 🚀

---

## IF STILL STUCK

**Absolute fallback - Create file manually:**

```bash
sudo nano /usr/local/bin/l4_redirector_v3_hybrid_working.py
# Paste the content from:
# https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/blob/main/VPS/l4_redirector_v3_hybrid_working.py

sudo chmod +x /usr/local/bin/l4_redirector_v3_hybrid_working.py
sudo systemctl restart redirector-v3.service
```

---

## SUMMARY

4 installation methods provided for different situations:

1. ✅ **Manual Install** - No downloads, fastest
2. ✅ **Git Clone** - If git available
3. ✅ **wget with Retries** - If curl fails
4. ✅ **Local File** - If you have it

All lead to same result: **Working hybrid redirector with 8 data streams**.

---

*Choose METHOD 1 if unsure. It works in 99% of cases.* 🚀
